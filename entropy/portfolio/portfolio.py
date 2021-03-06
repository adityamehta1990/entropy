'''Portfolio class (inherits from CompositeAsset)'''
from functools import lru_cache
import numpy as np
import pandas as pd
import entropy.asset.constants as ac
import entropy.portfolio.constants as pc
import entropy.asset.assetData as assetData
from entropy.asset.compositeAsset import CompositeAsset
import entropy.utils.timeseries as tsu
from entropy.analytics import analytics

class Portfolio(CompositeAsset):
    '''Portfolio (inherits from CompositeAsset)
    Implements nav, holdings
    '''
    def portfolioData(self):
        data = self.client.portfolioData({pc.PORTFOLIO_ID: self.Id}, {pc.TRANSACTIONS: 0})
        if data.count() != 1:
            raise RuntimeError('Could not find portfolio data for id: {}'.format(self.Id))
        return data[0]

    def isSavedAsset(self):
        return False

    def transactions(self):
        data = self.client.portfolioData({pc.PORTFOLIO_ID: self.Id}, {pc.TRANSACTIONS: 1})
        if data.count() != 1:
            raise RuntimeError('Could not find portfolio transactions for id: {}'.format(self.Id))
        return data[0][pc.TRANSACTIONS]

    # there can be multiple transactions in same fund on same date
    # this leads to duplicate entries while creating index from txn date
    # in any case, we should sum up txns made on the same day
    def _aggTxns(self):
        txns = pd.DataFrame(self.transactions())
        return txns.groupby([pc.TXN_DATE, pc.ASSET_CODE, pc.ASSET_NAME], as_index=False).sum()

    def holdingsIds(self):
        return list(set([txn[pc.ASSET_CODE] for txn in self.transactions()]))

    def holdings(self):
        df = pd.DataFrame(assetData.assetInfo(self.client, self.holdingsIds(), keys=ac.ASSET_ATTRIBUTES))
        df = df.rename(columns={ac.ASSET_ID: pc.ASSET_CODE}).set_index(pc.ASSET_CODE)
        # todo: separate this in a different fn where we can also get aggregate CFs, qty, etc
        # and not just latest exposure
        wts = self.holdingsExposure().iloc[-1]
        wts.name = pc.HOLDINGS_EXPOSURE
        return df.join(wts)

    def holdingsCF(self):
        txns = self._aggTxns()
        cf = txns.pivot(columns=pc.ASSET_CODE, values=pc.TXN_CASHFLOW, index=pc.TXN_DATE)
        cf.index.rename(None, inplace=True)
        return tsu.dailySum(cf)

    def holdingsQty(self):
        txns = self._aggTxns()
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

    @lru_cache()
    def nav(self):
        hAUM = self.holdingsAUM()
        nav = hAUM.fillna(method='ffill').sum(axis=1)
        # nullifying when all fund prices as nulls - do we really have to?
        # is there a better way?
        nav[hAUM.sum(axis=1).isnull()] = np.nan
        return nav.to_frame(name=self.Id)

# todo
# tables of stats
# excess returns
# portfolio Vol (rolling if possible)
# mean var opt (with select funds) - take risk profile as inputs

# Charts
# CF (monthly agg) bar chart
# One chart per benchmark (cum pnls along with their benchmark cum pml)
# Asset Class Agg cum pnl 
# Portfolio cum pnl + hypothetical portfolio benchmark
# Pie of allocation
