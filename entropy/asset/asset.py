from abc import ABCMeta
from abc import abstractmethod
import pandas as pd
import six
from entropy import analytics
from entropy.asset import assetData
from bson.objectid import ObjectId

# base class for any type of asset/investment - fund, stock, bond
# this can implement returns and risk based analytics

@six.add_metaclass(ABCMeta)
class Asset():
    # every asset must have the following:
    client = None   # db client
    mongoId = None  # mongoID for assets in assetMetaDataColl
    Id = None       # unique ID for all assets, MUST be a hexstring
    isCompositeAsset = False

    def __init__(self,Id,client):
        self.client = client
        self.Id = str(Id)               # typecasting, in case it isn't a string
        self.mongoId = ObjectId(Id)     # not used for assets not in assetMetaDataColl

    # values for base assets are stored not derived
    def nav(self):
        data = [v for v in assetData.valuesById(self.client, self.mongoId)]
        values = [v.get(self.Id) for v in data]
        dates = [v[assetData.VALUE_DATE] for v in data]
        nav = pd.Series(values, dates)
        return nav.dropna().sort_index()
    
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
