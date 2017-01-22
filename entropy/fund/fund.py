from entropy.investment import Investment
from entropy.fund import fundData
from bson.objectid import ObjectId
import pandas as pd
import re

class Fund(Investment):
    idStr = None # string rep of MONGO_ID for this fund
    _id = None # MONGO_ID for this fund
    client = None # db client

    def __init__(self,idStr,client):
        self.client = client
        # it is expected to get string in idStr because it will be passed in a http request
        # but it does not hurt to typecast
        self.idStr = str(idStr)
        self._id = ObjectId(idStr)

    def nav(self):
        return fundData.fundNAV(self.client, self.idStr)

    # can implement dividend into this
    # for now, cashflow for fund is empty
    def cashflow(self):
        return pd.Series([], [])

    def fundInfo(self):
        info = dict.fromkeys(fundData.FUND_ATTRIBUTES)
        info.update(fundData.fundInfo(self.client, self._id))
        return info
