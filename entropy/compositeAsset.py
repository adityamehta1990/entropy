from abc import ABCMeta
from abc import abstractmethod
from entropy import analytics
import pandas as pd

# base class for investments/assets which are a set of assets themselves
# such as portfolio, fund, and benchmarks
# this can implement holdings based analytics

class CompositeAsset(metaclass=ABCMeta):
    isCompositeAsset = True

    # todo: uncomment after implementing holdings in portfolio and fund
    # @abstractmethod
    def holdings(self):
        pass

    def explodedHoldings(self):
        pass
