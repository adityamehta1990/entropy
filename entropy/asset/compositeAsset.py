'''Composite assets are assets which can hold other assets
These include funds, benchmarks and portfolios
'''
from abc import ABCMeta
from functools import lru_cache
import six
from entropy.asset.asset import Asset

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

    @lru_cache()
    def holdingsNav(self):
        return self._navFromIds(self.holdingsIds())

    def holdingsQty(self):
        pass

    # @abstractmethod
    def holdings(self):
        pass

    def explodedHoldings(self):
        pass
