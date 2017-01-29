from abc import ABCMeta
from abc import abstractmethod
import pandas as pd
import six
from entropy import analytics
from entropy.asset import assetData

# base class for any type of asset/investment - fund, stock, bond
# this can implement returns and risk based analytics

@six.add_metaclass(ABCMeta)
class Asset():
    # every asset must have the following:
    client = None   # db client
    Id = None       # unique ID for all assets, MUST be a hexstring
    isCompositeAsset = False

    def __init__(self,Id,client):
        self.client = client
        self.Id = str(Id)               # typecasting, in case it isn't a string

    def isSavedAsset(self):
        return len(self.Id) == 24

    def assetInfo(self, keys=[]):
        if not self.isSavedAsset():
            raise "Must NOT invoke asset info on " + type(self)
        return assetData.assetInfo(self.client, [self.Id], keys)[0]

    # retrives NAV stored in database
    def _navFromIds(self,Ids):
        data = assetData.values(self.client,Ids)
        values = [dict([(Id,v.get(Id)) for Id in Ids]) for v in data]
        dates = [v[assetData.VALUE_DATE] for v in data]
        nav = pd.DataFrame(values, index=dates)
        # todo: align it to daily after sorting?
        return nav.sort_index() # caveat: don't drop na

    # values for base assets are stored not derived
    def nav(self):
        return self._navFromIds([self.Id])
    
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
