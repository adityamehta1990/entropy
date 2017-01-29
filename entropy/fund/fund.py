import pandas as pd
import re
from entropy.asset.compositeAsset import CompositeAsset
from entropy.fund import fundData

class Fund(CompositeAsset):

    def nav(self):
        return super(Fund, self).nav()

    # can implement dividend into this
    # for now, cashflow for fund is empty
    def cashflow(self):
        return pd.Series([], [])

    def fundInfo(self):
        # this will keep missing keys with nones
        info = dict.fromkeys(fundData.FUND_ATTRIBUTES)
        info.update(self.assetInfo(fundData.FUND_ATTRIBUTES))
        return info
