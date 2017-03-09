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
        'TRADE_DATE', 'TRANSACTION_TYPE', 'DIVIDEND_RATE', 'AMOUNT', 'UNITS', 'PRICE', 'BROKER']

KARVY_TXN_COLS = ['FundName', 'Investor Name', 'Account Number', 'Product Code',\
    'Scheme Description', 'Transaction Date', 'Transaction Description', 'Amount',\
    'Units', 'NAV', 'Broker Code', 'Broker Name', 'SchemeISIN']

KARVY_CAMS_COL_MAP = {
    'FundName': 'MF_NAME',
    'Scheme Description': 'SCHEME_NAME',
    'Transaction Date': 'TRADE_DATE',
    'Transaction Description': 'TRANSACTION_TYPE',
    'Amount': 'AMOUNT',
    'Units': 'UNITS',
    'NAV': 'PRICE'
}

# CAMS has some registration related transactions :/
# KARVY is missing dividends :/
FILTER_OUT_TXN_TYPES = [
    'address updated from kra',
    'registration of nominee',
    'registered'
]

# unused as of now
TXN_TYPES = ['purchase', 'dividend reinvested', 'dividend paid out', 'switch in', 'switch out',\
        'redemption', 'address', 'registered']

def importFundTransactionsFromFile(client, portfolioId, file):
    fileName = file if isinstance(file, str) else file.filename
    if fileName.endswith('xls'):
        df = pd.read_excel(file)
    elif fileName.endswith('csv'):
        df = pd.read_csv(file)
    else:
        raise RuntimeError('Unknown file type')
    if list(df.columns) == KARVY_TXN_COLS:
        df = df.rename(columns=KARVY_CAMS_COL_MAP)
    elif list(df.columns) != CAMS_TXN_COLS:
        raise Exception('Cannot parse uploaded transaction file')
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    # get valid txns
    txns = df[df.apply(lambda x: not match.matchAnyIdentifier(x.TRANSACTION_TYPE,\
            FILTER_OUT_TXN_TYPES), axis=1)]
    funds = fundData.fundList(client)
    txnsToAdd = []
    failedTxns = []
    # grouping because there can be many transactions per fund
    for (key, txnGrp) in txns.groupby(['MF_NAME', 'SCHEME_NAME']):
        fundISIN = txnGrp.iloc[0].get('SchemeISIN')
        if fundISIN:
            fund = [f for f in funds if f[fc.ISIN] == fundISIN][0]
        else:
            try:
                isCloseEnded = any([x.lower().find('nfo') > -1 for x in set(txns.TRANSACTION_TYPE)])
                txnInfo = {
                    fc.FUND_NAME_AMFI: fundData.fundNameProcessor(key[1]),
                    fc.FUND_HOUSE: key[0],
                    fc.FUND_TYPE: 'close ended schemes' if isCloseEnded else 'open ended schemes'
                }
                txnInfo = fundData.enrichFundInfo(txnInfo)
                fund = match.matchDictBest(txnInfo, funds, ac.ASSET_NAME, scorer=fuzz.token_sort_ratio)
                # fall back to token set if token sort doesnt work
                if not fund:
                    fund = match.matchDictBest(txnInfo, funds, ac.ASSET_NAME, scorer=fuzz.token_set_ratio)
            except Exception:
                failedTxns = failedTxns + txnGrp.to_dict('records')
                continue
        fundId = str(fund[dbclient.MONGO_ID])
        # the txn ID is dummy here, gets correctly calced in addManyTransactions
        for txn in txnGrp.itertuples():
            txnsToAdd.append(portfolioData.newTransaction(0, fundId, fund[ac.ASSET_NAME],\
                txn.AMOUNT, txn.UNITS, dtu.parse(txn.TRADE_DATE), txn.TRANSACTION_TYPE))
        print('processed {}'.format(fund[ac.ASSET_NAME]))
    ack = portfolioData.addManyTransactions(client, portfolioId, txnsToAdd)
    if not ack:
        print('Failed to store transactions in db')
    return failedTxns
