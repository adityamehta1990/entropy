import pandas as pd
import re
from entropy.db import dbclient
from entropy.asset import assetData
import entropy.fund.constants as fc
# define schema, possible values, etc

def fundList(client, navDate=None):
    keys = dict([(key, 1) for key in fc.FUND_ATTRIBUTES])
    funds = [f for f in client.assetMetaData({fc.ASSET_TYPE_KEY : fc.ASSET_TYPE}, keys)]
    if navDate is not None:
        vals = assetData.valuesOnDate(client, navDate)
        funds = [f for f in funds if vals.get(str(f[dbclient.MONGO_ID])) is not None]
    return funds

# todo: add test: Fund(fundIdFromAmfiCode(client,'125494'),client).fundInfo()[FUND_CODE_AMFI] == '125494'
def fundIdFromAmfiCode(client, amfiCode):
    data = client.assetMetaData({fc.ASSET_TYPE_KEY : fc.ASSET_TYPE, \
                                 fc.FUND_CODE_AMFI : amfiCode}, {fc.FUND_CODE_AMFI : 1})
    assert data.count() == 1, "Invalid amfi code"
    return str(data[0][dbclient.MONGO_ID])

# check what got passed in from fundInfo
def checkFundAttributes(fundInfo):
    wrongKeys = [key for key in fundInfo.keys() if key not in fc.FUND_ATTRIBUTES]
    if len(wrongKeys):
        raise Exception('{} are not a valid calculated fund attribute(s)'.format(','.join(wrongKeys)))
    return True

# fundInfo can be passed back from website or can be "enriched"
def updateFundInfo(client, Id, fundInfo):
    checkFundAttributes(fundInfo)
    # now store
    return assetData.updateAssetInfo(client, Id, fundInfo)

# map values from amfi codes to internal IDs and update for given date
def updateFundNAVOnDate(client, dt, valueMap):
    return assetData.updateValuesOnDate(client, dt, valueMap, fc.ASSET_TYPE, fc.FUND_CODE_AMFI)

# only enrich missing data
def enrichedFundInfo(client, Id):
    info = assetData.assetInfo(client, Id)
    enrichedInfo = {}
    nameParts = [part.strip() for part in info[fc.FUND_NAME_AMFI].split('-')]
    # amfi info based enrichment logic
    if not info.get(fc.FUND_NAME):
        pattern = re.compile('|'.join(fc.FUND_RETURN_OPTIONS + fc.FUND_INVESTMENT_OPTIONS), re.IGNORECASE)
        enrichedInfo[fc.FUND_NAME] = '-'.join(filter(lambda x: not pattern.search(x), nameParts))
    if not info.get(fc.IS_OPEN_ENDED):
        enrichedInfo[fc.IS_OPEN_ENDED] = re.compile('open ended scheme', re.IGNORECASE).search(info[fc.FUND_TYPE]) is not None
    if not info.get(fc.IS_DIRECT):
        enrichedInfo[fc.IS_DIRECT] = re.compile('direct', re.IGNORECASE).search(info[fc.FUND_NAME_AMFI]) is not None
    if not info.get(fc.HAS_DIVIDEND):
        enrichedInfo[fc.HAS_DIVIDEND] = re.compile('dividend', re.IGNORECASE).search(info[fc.FUND_NAME_AMFI]) is not None
    return enrichedInfo
