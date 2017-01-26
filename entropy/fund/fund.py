from entropy.asset.compositeAsset import CompositeAsset
from entropy.fund import fundData
import pandas as pd
import re

class Fund(CompositeAsset):

    def nav(self):
        return super(Fund, self).nav()

    # can implement dividend into this
    # for now, cashflow for fund is empty
    def cashflow(self):
        return pd.Series([], [])

    def fundInfo(self):
        info = dict.fromkeys(fundData.FUND_ATTRIBUTES)
        info.update(fundData.fundInfo(self.client, self.mongoId))
        return info
