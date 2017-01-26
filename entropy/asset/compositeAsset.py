from abc import ABCMeta
from abc import abstractmethod
from asset import Asset
import pandas as pd
import six

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

    # todo: uncomment after implementing holdings in portfolio and fund
    # @abstractmethod
    def holdings(self):
        pass

    def explodedHoldings(self):
        pass
