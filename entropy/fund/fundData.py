import pandas as pd
import re
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

FUND_RETURN_OPTIONS = ['growth', 'dividend']
FUND_INVESTMENT_OPTIONS = ['direct', 'regular']

IS_OPEN_ENDED = 'isOpenEnded'
HAS_DIVIDEND = 'hasDividend'
DIVIDEND_PERIOD = 'hasDividend'
IS_DIRECT = 'isDirect'

FUND_ATTRIBUTES_AMFI = [FUND_NAME_AMFI, FUND_CODE_AMFI, FUND_HOUSE, FUND_TYPE]
FUND_ATTRIBUTES_CALC = [FUND_NAME, IS_OPEN_ENDED, HAS_DIVIDEND, DIVIDEND_PERIOD, IS_DIRECT]
FUND_ATTRIBUTES_INPUT = list(FUND_CLASSIFICATION.keys()) + \
                        list(FUND_ATTRIBUTES_EQUITY.keys()) + \
                        list(FUND_ATTRIBUTES_DEBT.keys())

FUND_ATTRIBUTES = FUND_ATTRIBUTES_AMFI + FUND_ATTRIBUTES_CALC

def fundList(client, navDate=None):
    keys = dict([(key,1) for key in FUND_ATTRIBUTES])
    funds = [f for f in client.fundData({}, keys)]
    if navDate is not None:
        vals = client.valueDataOnDate(navDate)
        funds = [f for f in funds if vals.get(str(f[dbclient.MONGO_ID])) is not None]
    return funds

def fundInfo(client, _id):
    keys = dict([(key,1) for key in FUND_ATTRIBUTES])
    data = client.fundData({dbclient.MONGO_ID: _id}, keys)
    if( data.count() == 1 ):
        data = data[0]
    else:
        data = {}
    return data

# fundInfo can be passed back from website or can be "enriched"
def updateFundInfo(client, _id, fundInfo):
    # check what got passed in from fundInfo
    wrongKeys = [ key for key in fundInfo.keys() if key not in FUND_ATTRIBUTES ]
    if len(wrongKeys):
        raise Exception('{} are not a valid calculated fund attribute(s)'.format(','.join(wrongKeys)))
    # now store
    return client.updateFundData({dbclient.MONGO_ID: _id}, fundInfo)

def fundNAV(client, _id):
    data = [v for v in client.valueDataById(_id)]
    idStr = str(_id)
    values = [v.get(idStr) for v in data]
    dates = [v["valueDate"] for v in data]
    nav = pd.Series(values, dates)
    return nav.dropna().sort_index()

# merge and override fund NAV for date
def updateFundNAV(client, dt, valueMap):
    fundCodeMap = client.fundData({}, {FUND_CODE_AMFI:1})
    newValueMap = {}
    for fund in fundCodeMap:
        if valueMap.get(fund[FUND_CODE_AMFI]) is not None:
            newValueMap[str(fund[dbclient.MONGO_ID])] = valueMap[fund[FUND_CODE_AMFI]]
    return client.updateValueData(dt, dict(newValueMap))

# only enrich missing data
def enrichedFundInfo(client, _id):
    info = fundInfo(client, _id)
    enrichedInfo = {}
    nameParts = [part.strip() for part in info[FUND_NAME_AMFI].split('-')]
    # amfi info based enrichment logic
    if not info.get(FUND_NAME):
        pattern = re.compile('|'.join(FUND_RETURN_OPTIONS + FUND_INVESTMENT_OPTIONS), re.IGNORECASE)
        enrichedInfo[FUND_NAME] = '-'.join(filter(lambda x: not pattern.search(x), nameParts))
    if not info.get(IS_OPEN_ENDED):
        enrichedInfo[IS_OPEN_ENDED] = re.compile('open ended scheme',re.IGNORECASE).search(info[FUND_TYPE]) is not None
    if not info.get(IS_DIRECT):
        enrichedInfo[IS_DIRECT] = re.compile('direct',re.IGNORECASE).search(info[FUND_NAME_AMFI]) is not None
    if not info.get(HAS_DIVIDEND):
        enrichedInfo[HAS_DIVIDEND] = re.compile('dividend',re.IGNORECASE).search(info[FUND_NAME_AMFI]) is not None
    return enrichedInfo
