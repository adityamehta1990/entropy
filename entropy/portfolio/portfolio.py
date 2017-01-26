import datetime
import pandas as pd
from entropy.fund import fundData
from entropy.fund.fund import Fund
from entropy.investment import Investment
import constants

# todo : replace all strings with constants

class Portfolio(Investment):
    portfolioId=None
    client=None

    def __init__(self, portfolioId, client):
        self.portfolioId = portfolioId
        self.client = client

    def portfolioData(self):
        data = self.client.portfolioData({constants.PORTFOLIO_ID : self.portfolioId}, {constants.TRANSACTIONS : 0})
        if(data.count() == 1):
            P = data[0]
        else:
            P = {}
        return P

    def transactions(self):
        data = self.client.portfolioData({constants.PORTFOLIO_ID : self.portfolioId})
        if(data.count() == 1):
            Ts = data[0][constants.TRANSACTIONS]
        else:
            Ts = []
        return Ts

    # todo: add composite asset class which has exploded holdings
    # this is really holdings/investments
    def aggregateTxns(self):
        txns = pd.DataFrame(self.transactions())
        # first aggregate qty and cf by date+schemeCode to handle multiple txns on a date
        aggTxns = txns.groupby(by=[constants.TXN_DATE, constants.ASSET_CODE]) \
            .agg({constants.TXN_CASHFLOW : sum, constants.TXN_QUANTITY : sum})
        cumAggTxns = aggTxns.groupby(level=constants.ASSET_CODE) \
            .cumsum() \
            .rename(columns={constants.TXN_CASHFLOW : 'cum_cashflow', constants.TXN_QUANTITY : 'cum_quantity'})
        # concat cum by index and reset to date index
        return pd.concat([aggTxns, cumAggTxns], axis=1).reset_index(level=constants.ASSET_CODE)

    # actual market value of portfolio
    def marketValue(self):
        aggTxns = self.aggregateTxns()
        # front fill by padding so that there are only leading NAs
        qty = aggTxns.pivot(columns=constants.ASSET_CODE, values='cum_quantity') \
            .fillna(method='pad')
        # generate empty mv curve from first txn to today
        index = pd.DatetimeIndex(freq='D', start=qty.first_valid_index(), end=datetime.datetime.today())
        mv = pd.Series(index=index).fillna(0)
        qty = qty.reindex(index=index, method='pad').fillna(0) # now fillna zero for initial period
        # add conditions here based on asset type. for now all assets are funds
        for (assetCode, assetQty) in qty.iteritems():
            assetValue = Fund(assetCode, self.client).nav()
            # dont fillna here, if fund nav is missing, it should yield NaN
            mv = mv.add(assetQty * assetValue)
        return mv.dropna()

    # portfolio value if you had invested one rupee at the start
    # and received the same returns. basically compounded at TWRR
    def nav(self):
        mv = self.marketValue()
        ts = mv - self.cashflow().reindex(mv.index).fillna(0)
        # only first value will be NaN because of the shift
        return (ts / mv.shift(1)).fillna(1).cumprod()

    # todo: add options for groupby, cumulative and send back to FE
    def cashflow(self):
        aggTxns = self.aggregateTxns()
        return pd.Series(aggTxns.groupby(level='date').sum().cashflow)
