import pandas as pd
import re
from entropy.asset.compositeAsset import CompositeAsset
import entropy.fund.constants as fc

class Fund(CompositeAsset):

    def nav(self):
        return super(Fund, self).nav()

    # can implement dividend into this
    # for now, cashflow for fund is empty
    def cashflow(self):
        return pd.Series([], [])

    def fundInfo(self):
        # this will keep missing keys with nones
        info = dict.fromkeys(fc.FUND_ATTRIBUTES)
        info.update(self.assetInfo(fc.FUND_ATTRIBUTES))
        return info
