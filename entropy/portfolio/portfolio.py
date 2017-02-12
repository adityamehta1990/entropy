import datetime
import pandas as pd
from entropy.fund.fund import Fund
import entropy.fund.constants as fc
import entropy.portfolio.constants as pc
import entropy.asset.assetData as assetData
from entropy.asset.compositeAsset import CompositeAsset
import entropy.utils.timeseries as tsu
import numpy as np
from entropy.analytics import analytics

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

    def holdingsCF(self):
        txns = pd.DataFrame(self.transactions())
        cf = txns.pivot(columns=pc.ASSET_CODE, values=pc.TXN_CASHFLOW, index=pc.TXN_DATE)
        cf.index.rename(None, inplace=True)
        return tsu.dailySum(cf)

    def holdingsQty(self):
        txns = pd.DataFrame(self.transactions())
        qty = txns.pivot(columns=pc.ASSET_CODE, values=pc.TXN_QUANTITY, index=pc.TXN_DATE)
        qty.index.rename(None, inplace=True)
        # todo: only temporarily compute by CF, remove this line later
        # qty = self.holdingsCF() / self.holdingsNav()
        return tsu.alignToRegularDates(tsu.dailySum(qty).cumsum()).fillna(method='ffill')

    def holdingsAUM(self):
        hNav = self.holdingsNav()
        hQty = self.holdingsQty().reindex(index=hNav.index, method='ffill')
        return tsu.dropInitialNa(hQty * hNav)

    def holdingsExposure(self):
        return self.holdingsAUM().fillna(method='ffill').divide(self.nav().iloc[:, 0], axis='index')

    # move to CompositeAsset class
    def holdingsReturn(self):
        return analytics.dailyReturn(self.holdingsNav())

    def dailyReturn(self):
        exposure = self.holdingsExposure().fillna(method='ffill')
        return (exposure.shift() * self.holdingsReturn()).sum(axis=1).to_frame(name=self.Id)

    def nav(self):
        hAUM = self.holdingsAUM()
        nav = hAUM.fillna(method='ffill').sum(axis=1)
        # nullifying when all fund prices as nulls - do we really have to?
        # is there a better way?
        nav[hAUM.sum(axis=1).isnull()] = np.nan
        return nav.to_frame(name=self.Id)
