import pandas as pd
import re
from entropy.db import dbclient
from entropy.asset import assetData
# define schema, possible values, etc

# todo: rename to fundio and move fund stuff from dbio here

# we get raw data from amfi, which can be parsed to enrich meta data about a fund
FUND_NAME = "fundName"
FUND_NAME_AMFI = "fundNameRaw"
FUND_CODE_AMFI = "amfiCode"
FUND_HOUSE = "fundHouse"

FUND_TYPE = "fundType"
FUND_TYPE_CHOICES = ["open ended", "close ended", "interval"]

ISIN = "ISIN"
ASSET_TYPE = "fund"
ASSET_CLASS = "assetClass"
STRATEGY_TYPE = "strategyType" # this is a short hand for investment attributes

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

FUND_ATTRIBUTES_AMFI = [FUND_NAME_AMFI, FUND_CODE_AMFI, FUND_HOUSE, FUND_TYPE, ISIN]
FUND_ATTRIBUTES_CALC = [FUND_NAME, IS_OPEN_ENDED, HAS_DIVIDEND, DIVIDEND_PERIOD, IS_DIRECT]
FUND_ATTRIBUTES_INPUT = list(FUND_CLASSIFICATION.keys()) + \
                        list(FUND_ATTRIBUTES_EQUITY.keys()) + \
                        list(FUND_ATTRIBUTES_DEBT.keys())

FUND_ATTRIBUTES = FUND_ATTRIBUTES_AMFI + FUND_ATTRIBUTES_CALC

def fundList(client, navDate=None):
    keys = dict([(key, 1) for key in FUND_ATTRIBUTES])
    funds = [f for f in client.assetMetaData({assetData.ASSET_TYPE_KEY : ASSET_TYPE}, keys)]
    if navDate is not None:
        vals = client.valueDataOnDate(navDate)
        funds = [f for f in funds if vals.get(str(f[dbclient.MONGO_ID])) is not None]
    return funds

# todo: add test: Fund(fundIdFromAmfiCode(client,'125494'),client).fundInfo()[FUND_CODE_AMFI] == '125494'
def fundIdFromAmfiCode(client, schemeCode):
    data = client.assetMetaData({assetData.ASSET_TYPE_KEY : ASSET_TYPE, \
                                 FUND_CODE_AMFI : schemeCode}, {FUND_CODE_AMFI : 1})
    assert data.count() == 1, "Invalid schemeCode"
    return str(data[0][dbclient.MONGO_ID])

# fundInfo can be passed back from website or can be "enriched"
def updateFundInfo(client, mongoId, fundInfo):
    # check what got passed in from fundInfo
    wrongKeys = [key for key in fundInfo.keys() if key not in FUND_ATTRIBUTES]
    if len(wrongKeys):
        raise Exception('{} are not a valid calculated fund attribute(s)'.format(','.join(wrongKeys)))
    # now store
    return client.updateAssetMetaData({dbclient.MONGO_ID: mongoId}, fundInfo)

# map values from amfi codes to internal IDs and update for given date
def updateFundNAVOnDate(client, dt, valueMap):
    fundCodeMap = client.assetMetaData({assetData.ASSET_TYPE_KEY : ASSET_TYPE}, {FUND_CODE_AMFI:1})
    newValueMap = {}
    for fund in fundCodeMap:
        if valueMap.get(fund[FUND_CODE_AMFI]) is not None:
            newValueMap[str(fund[dbclient.MONGO_ID])] = valueMap[fund[FUND_CODE_AMFI]]
    return assetData.updateValueDataOnDate(client, dt, dict(newValueMap))

# only enrich missing data
def enrichedFundInfo(client, mongoId):
    info = assetData.assetInfoById(client, mongoId)
    enrichedInfo = {}
    nameParts = [part.strip() for part in info[FUND_NAME_AMFI].split('-')]
    # amfi info based enrichment logic
    if not info.get(FUND_NAME):
        pattern = re.compile('|'.join(FUND_RETURN_OPTIONS + FUND_INVESTMENT_OPTIONS), re.IGNORECASE)
        enrichedInfo[FUND_NAME] = '-'.join(filter(lambda x: not pattern.search(x), nameParts))
    if not info.get(IS_OPEN_ENDED):
        enrichedInfo[IS_OPEN_ENDED] = re.compile('open ended scheme', re.IGNORECASE).search(info[FUND_TYPE]) is not None
    if not info.get(IS_DIRECT):
        enrichedInfo[IS_DIRECT] = re.compile('direct', re.IGNORECASE).search(info[FUND_NAME_AMFI]) is not None
    if not info.get(HAS_DIVIDEND):
        enrichedInfo[HAS_DIVIDEND] = re.compile('dividend', re.IGNORECASE).search(info[FUND_NAME_AMFI]) is not None
    return enrichedInfo
