'''Upload transactions using csv'''
import pandas as pd
from fuzzywuzzy import fuzz
from entropy.fund import fundData
from entropy.portfolio import portfolioData
from entropy.utils import match
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu
import entropy.asset.constants as ac
import entropy.fund.constants as fc

CAMS_TXN_COLS = ['MF_NAME', 'INVESTOR_NAME', 'PAN', 'FOLIO_NUMBER', 'PRODUCT_CODE', 'SCHEME_NAME',\
        'TRADE_DATE', 'TRANSACTION_TYPE', 'DIVIDEND_RATE' 'AMOUNT', 'UNITS', 'PRICE', 'BROKER']

FILTER_OUT_TXN_TYPES = [
    'address updated from kra',
    'registration of nominee',
    'registered'
]
TXN_TYPES = ['purchase', 'dividend reinvested', 'dividend paid out', 'switch in', 'switch out',\
        'redemption', 'address', 'registered']

def importFundTransactionsFromFile(client, portfolioId, fileName):
    if fileName.endswith('xls'):
        df = pd.read_excel(fileName)
    elif fileName.endswith('csv'):
        df = pd.read_csv(fileName)
    else:
        raise RuntimeError('Unknown file type')
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    # get valid txns
    txns = df[df.apply(lambda x: not match.matchAnyIdentifier(x.TRANSACTION_TYPE, FILTER_OUT_TXN_TYPES), axis=1)]
    funds = fundData.fundList(client)
    txnsToAdd = []
    failedTxns = []
    # grouping because there can be many transactions per fund
    for (key, txnGrp) in txns.groupby(['MF_NAME', 'SCHEME_NAME']):
        isCloseEnded = any([x.lower().find('nfo') > -1 for x in set(txns.TRANSACTION_TYPE)])
        txnInfo = {
            fc.FUND_NAME_AMFI: fundData.fundNameProcessor(key[1]),
            fc.FUND_HOUSE: key[0],
            fc.FUND_TYPE: 'close ended schemes' if isCloseEnded else 'open ended schemes'
        }
        txnInfo = fundData.enrichFundInfo(txnInfo)
        try:
            fund = match.matchDictBest(txnInfo, funds, ac.ASSET_NAME, scorer=fuzz.token_sort_ratio)
            # fall back to token set if token sort doesnt work
            if not fund:
                fund = match.matchDictBest(txnInfo, funds, ac.ASSET_NAME, scorer=fuzz.token_set_ratio)
            fundId = str(fund[dbclient.MONGO_ID])
            # the txn ID is dummy here, gets correctly calced in addManyTransactions
            for txn in txnGrp.itertuples():
                txnsToAdd.append(portfolioData.newTransaction(0, fundId, fund[ac.ASSET_NAME],\
                    txn.AMOUNT, txn.UNITS, dtu.parse(txn.TRADE_DATE), txn.TRANSACTION_TYPE))
            print('processed {}'.format(txnInfo[ac.ASSET_NAME]))
        except Exception:
            failedTxns = failedTxns + txnGrp.to_dict('records')
    ack = portfolioData.addManyTransactions(client, portfolioId, txnsToAdd)
    if not ack:
        print('Failed to store transactions in db')
    return failedTxns
