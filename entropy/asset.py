from abc import ABCMeta
from abc import abstractmethod
from entropy import analytics
import pandas as pd

# base class for any type of asset/investment - fund, stock, bond
# this can implement returns and risk based analytics

ASSET_ATTRIBUTES = ['assetType', 'assetClass']

class Asset(metaclass=ABCMeta):
    isCompositeAsset = False

    @abstractmethod
    # this should not include cashflow
    def nav(self):
        pass

    @abstractmethod
    def cashflow(self):
        pass

    # daily return curve, optionally adjusted by cashflows
    def returns(self):
        return analytics.rollingReturn(self.nav(),'1D').fillna(0)

    # optional: can add total returns for dividends (cashflow)

    # YTD, MTD, 1y, 3y, SI etc
    def returnStats(self):
        returns = self.returns()
        return {
            'MTD': analytics.cumReturn( returns.last('M') ),
            'QTD': analytics.cumReturn( returns.last('Q') ),
            'YTD': analytics.cumReturn( returns.last('A') ),
            'SI': analytics.cumReturn(returns),
            '1Y': analytics.periodReturn(returns,'1Y'),
            '3Y': analytics.periodReturn(returns,'3Y'),
            '5Y': analytics.periodReturn(returns,'5Y')
        }

    # monthly/yearly returns
    def calendarPeriodReturns(self,type='month'):
        ret = self.returns()
        return analytics.calendarPeriodReturns(ret,type)

    # todo: internal rate of return

    # rolling return curve
    def rollingReturn(self,window='1D'):
        return analytics.rollingReturn(self.nav(),window).dropna()
