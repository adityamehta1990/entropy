import datetime
import pandas as pd
from entropy.fund.fund import Fund
import entropy.fund.constants as fc
import entropy.portfolio.constants as pc
import entropy.asset.assetData as assetData
from entropy.asset.compositeAsset import CompositeAsset
from entropy.utils import utils

class Portfolio(CompositeAsset):

    def portfolioData(self):
        data = self.client.portfolioData({pc.PORTFOLIO_ID : self.Id}, {pc.TRANSACTIONS : 0})
        if data.count() == 1:
            P = data[0]
        else:
            P = {}
        return P

    def isSavedAsset(self):
        return False

    def transactions(self):
        data = self.client.portfolioData({pc.PORTFOLIO_ID : self.Id})
        if data.count() == 1:
            ts = data[0][pc.TRANSACTIONS]
        else:
            ts = []
        return ts

    def holdingsIds(self):
        return list(set([txn[pc.ASSET_CODE] for txn in self.transactions()]))

    def holdings(self):
        keys = [
            fc.ISIN,
            fc.ASSET_TYPE_FUND,
            fc.ASSET_CLASS,
            fc.STRATEGY_TYPE
        ]
        return assetData.assetInfo(self.client, self.holdingsIds(), keys=keys)

    def holdingsCFs(self):
        txns = pd.DataFrame(self.transactions())
        cf = txns.pivot(columns=pc.ASSET_CODE, values=pc.TXN_CASHFLOW, index=pc.TXN_DATE)
        cf.columns.name = None
        return utils.dailySum(cf)

    def holdingsQty(self):
        txns = pd.DataFrame(self.transactions())
        qty = txns.pivot(columns=pc.ASSET_CODE, values=pc.TXN_QUANTITY, index=pc.TXN_DATE)
        qty.index.name = None
        # todo: only temporarily compute by CFs, remove this line later
        qty = self.holdingsCFs() / self.holdingsNav()
        return utils.alignToRegularDates(utils.dailySum(qty).cumsum()).fillna(method='ffill')

    def holdingsAUM(self):
        return utils.dropInitialNa(self.holdingsQty() * self.holdingsNav())

    def nav(self):
        return self.holdingsAUM().sum(axis=1).to_frame(name=self.Id)
