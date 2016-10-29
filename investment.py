from abc import ABCMeta,abstractmethod
import analytics
import pandas as pd

# base class for any type of investment - portfolio, fund, etc
# this can implement common analytics for returns and risk

# make this abstract
class Investment(metaclass=ABCMeta):
    @abstractmethod
    # this should not include cashflow
    def nav(self):
        pass
    
    @abstractmethod
    def cashflow(self):
        pass
    
    # daily return curve, optionally adjusted by cashflows
    def returns(self):
        nav = self.nav().resample('D').pad()
        return analytics.rollingReturn(nav,'1d')
    
    # todo: can add total returns for dividends (cashflow)

    # YTD, MTD, 1y, 3y, SI
    # todo: make this analytics which takes either period or days and computes from NAV
    def returnStats(self):
        returns = self.returns() + 1
        return {
            'MTD': returns.last('MS').cumprod().values[-1] - 1,
            'QTD': returns.last('QS').cumprod().values[-1] - 1,
            'YTD': returns.last('AS').cumprod().values[-1] - 1,
            'SI': returns.cumprod().values[-1] - 1
            #'1Y': returns.last('1y').cumprod().values[-1] - 1,
            #'3Y': returns.last('AS').cumprod().values[-1] - 1,
            #'5Y': returns.last('AS').cumprod().values[-1] - 1
        }

    # todo: monthly and annual returns, internal rate of return

    # rolling return curve
    def rollingReturn(self,window='1d'):
        nav = self.nav().resample('D').pad()
        return analytics.rollingReturn(nav,window)