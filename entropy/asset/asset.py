from abc import ABCMeta
from abc import abstractmethod
import pandas as pd
import six
from entropy.analytics import analytics
from entropy.asset import assetData
import entropy.asset.constants as ac
import entropy.utils.timeseries as tsu
import entropy.analytics.constants as ayc

# base class for any type of asset/investment - fund, stock, bond
# this can implement returns and risk based analytics

@six.add_metaclass(ABCMeta)
class Asset():
    # every asset must have the following:
    client = None   # db client
    Id = None       # unique ID for all assets, MUST be a hexstring
    isCompositeAsset = False

    def __init__(self, Id, client):
        self.client = client
        self.Id = str(Id)               # typecasting, in case it isn't a string

    def isSavedAsset(self):
        return len(self.Id) == 24

    def assetInfo(self, keys=[]):
        if not self.isSavedAsset():
            raise NotImplementedError("Must NOT invoke asset info on " + type(self))
        return assetData.assetInfo(self.client, [self.Id], keys)[0]

    # retrives NAV stored in database
    def _navFromIds(self, Ids):
        # todo: have a start and end date?
        data = assetData.valuesByIds(self.client, Ids)
        values = [dict([(Id, v.get(Id)) for Id in Ids]) for v in data]
        dates = [v[ac.VALUE_DATE] for v in data]
        nav = pd.DataFrame(values, index=dates)
        return tsu.dropInitialNa(tsu.alignToRegularDates(nav.sort_index()))

    # values for base assets are stored not derived
    def nav(self):
        return self._navFromIds([self.Id])

    @abstractmethod
    def cashflow(self):
        pass

    def dailyReturn(self):
        return analytics.dailyReturn(self.nav())

    # optional: can add total returns for dividends (cashflow)

    # YTD, MTD, 1y, 3y, SI etc
    def returnStats(self):
        returns = self.dailyReturn()
        stats = {
            'MTD': analytics.aggReturn(returns, ayc.AGG_LAST_PERIOD, 'M').iloc[0],
            'QTD': analytics.aggReturn(returns, ayc.AGG_LAST_PERIOD, 'Q').iloc[0],
            'YTD': analytics.aggReturn(returns, ayc.AGG_LAST_PERIOD, 'A').iloc[0],
            #'SI': analytics.cumReturn(returns),
            #'1Y': analytics.periodReturn(returns,'1Y'),
            #'3Y': analytics.periodReturn(returns,'3Y'),
            #'5Y': analytics.periodReturn(returns,'5Y')
        }
        return stats

    def rollingReturn(self, window='1D'):
        return analytics.aggReturn(self.dailyReturn(), ayc.AGG_ROLLING, window, annualize=True)
