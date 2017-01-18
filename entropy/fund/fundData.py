import pandas as pd
from entropy.db import dbclient
# define schema, possible values, etc

# todo: rename to fundio and move fund stuff from dbio here

# we get raw data from amfi, which can be parsed to enrich meta data about a fund
FUND_NAME = "fundName"
FUND_NAME_AMFI = "fundNameRaw"
FUND_CODE_AMFI = "amfiCode"
FUND_HOUSE = "fundHouse"

FUND_TYPE = "fundType"
FUND_TYPE_CHOICES = ["open ended", "close ended", "interval"]

ASSET_CLASS = "assetClass"
STRATEGY_TYPE = "strategyType" # this is a short hand for investment attributes
INVESTMENT_ATTRIBUTES = "investmentAttributes"

FUND_CLASSIFICATION = {
    ASSET_CLASS : ['equity', 'debt', 'hybrid'],
    STRATEGY_TYPE : []
}

# these are the various investment attributes based on asset class
FUND_ATTRIBUTES_EQUITY = {
    'marketCap' : ['large', 'medium', 'small'],
    'investmentStyle' : ['value', 'growth', 'blend'],
    'sector' : ['multi'] # multi if no sector
}

FUND_ATTRIBUTES_DEBT = {
    'duration' : ['short', 'medium', 'long'],
    'creditQuality' :  ['high', 'medium', 'low'],
    'underlier' : ['gilt', 'corp', 'liquid']
}

FUND_ATTRIBUTES_AMFI = [FUND_NAME_AMFI, FUND_CODE_AMFI, FUND_HOUSE, FUND_TYPE]
FUND_ATTRIBUTES_CALC = [FUND_NAME,]
FUND_ATTRIBUTES = FUND_ATTRIBUTES_AMFI + FUND_ATTRIBUTES_CALC

def fundInfo(client, _id):
    keys = dict([(key,1) for key in FUND_ATTRIBUTES])
    data = client.fundData({dbclient.MONGO_ID: _id}, keys)
    if( data.count() == 1 ):
        data = data[0]
    else:
        data = {}
    return( data )

def fundNAV(client, _id):
    data = [v for v in client.valueDataById(_id)]
    idStr = str(_id)
    values = [v.get(idStr) for v in data]
    dates = [v["valueDate"] for v in data]
    nav = pd.Series(values, dates)
    return nav.dropna().sort_index()