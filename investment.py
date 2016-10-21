from abc import ABCMeta,abstractmethod
import analytics
import pandas as pd

# base class for any type of investment - portfolio, fund, etc
# this can implement common analytics for returns and risk

# make this abstract
class Investment(metaclass=ABCMeta):
    @abstractmethod
    def nav(self):
        pass
    
    @abstractmethod
    def cashflow(self):
        pass

    def returnStats(self):
        # this should give various period returns (YTD, MTD, 1y, 3y, SI, etc)
        pass

    def rollingReturn(self,window='1d',includeCashflow=False):
        ts = self.nav()
        if not includeCashflow:
            ts = ts - self.cashflow().reindex(ts.index,method='pad').fillna(0)
        return analytics.rollingReturn(ts,window)