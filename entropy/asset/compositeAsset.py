from abc import ABCMeta
from abc import abstractmethod
from entropy.asset.asset import Asset
import pandas as pd

# base class for investments/assets which are a set of assets themselves
# such as portfolio, fund, and benchmarks
# this can implement holdings based analytics

class CompositeAsset(Asset, metaclass=ABCMeta):
    isCompositeAsset = True

    # nav for composite asset is either stored or derived from its holdings/transaction history
    def nav(self):
        super(CompositeAsset, self).nav()

    def cashflow(self):
        pass

    # todo: uncomment after implementing holdings in portfolio and fund
    # @abstractmethod
    def holdings(self):
        pass

    def explodedHoldings(self):
        pass
