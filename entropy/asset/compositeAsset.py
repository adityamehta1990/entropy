from abc import ABCMeta
from abc import abstractmethod
import pandas as pd
import six
from entropy.asset.asset import Asset
import entropy.asset.assetData as assetData

# base class for investments/assets which are a set of assets themselves
# such as portfolio, fund, and benchmarks
# this can implement holdings based analytics

@six.add_metaclass(ABCMeta)
class CompositeAsset(Asset):
    isCompositeAsset = True

    # nav for composite asset is either stored or derived from its holdings/transaction history
    def nav(self):
        return super(CompositeAsset, self).nav()

    def cashflow(self):
        pass

    # @abstractmethod
    def holdingsIds(self):
        pass
    
    # nav is a series and this is a df
    # make both consistent and a share code
    def holdingsNav(self):
        holdingsIds = map(str,self.holdingsIds())
        data = assetData.valuesByIds(self.client,holdingsIds)
        values = [dict([(Id,v.get(Id)) for Id in holdingsIds]) for v in data]
        dates = [v[assetData.VALUE_DATE] for v in data]
        nav = pd.DataFrame(values, index=dates)
        return nav.sort_index() # caveat: don't drop na
        
    def holdingsQty(self):
        pass

    # todo: uncomment after implementing holdings in portfolio and fund
    # @abstractmethod
    def holdings(self):
        pass

    def explodedHoldings(self):
        pass
