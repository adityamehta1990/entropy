'''library to get/update/manipulate fund data'''
import re
from entropy.db import dbclient
from entropy.asset import assetData
import entropy.fund.constants as fc
import entropy.asset.constants as ac
from entropy.utils import match
# define schema, possible values, etc

def fundList(client, navDate=None):
    keys = dict([(key, 1) for key in fc.FUND_ATTRIBUTES])
    funds = assetData.assetList(client, fc.ASSET_TYPE_FUND, keys, navDate)
    return funds

# todo: add test: Fund(fundIdFromAmfiCode(client,'125494'),client).fundInfo()[FUND_CODE_AMFI] == '125494'
def fundIdFromAmfiCode(client, amfiCode):
    data = client.assetMetaData({fc.ASSET_TYPE_KEY : fc.ASSET_TYPE_FUND, \
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
    return assetData.updateValuesOnDate(client, dt, valueMap, fc.ASSET_TYPE_FUND, fc.FUND_CODE_AMFI)

def fundNameProcessor(fundName):
    '''for use in fuzzywuzzy or other fund name processing'''
    fundName = fundName.replace('option', 'plan')
    fundName = fundName.replace('regular', '').replace('standard', '')
    return fundName

# only enrich missing data
def enrichFundInfo(info):
    fundName = fundNameProcessor(info[fc.FUND_NAME_AMFI].lower())
    fundType = info[fc.FUND_TYPE].lower()
    nameParts = [part.strip() for part in fundName.split('-')]
    # amfi info based enrichment logic
    # strip out growth/div and direct plan info from fund name
    if not info.get(fc.FUND_NAME):
        if len(nameParts) > 1:
            pattern = re.compile('|'.join(fc.FUND_RETURN_OPTIONS + fc.FUND_MODES), re.IGNORECASE)
            info[fc.FUND_NAME] = ' '.join([x for x in nameParts if not pattern.search(x)])
        else:
            info[fc.FUND_NAME] = fundName
            for rem in fc.FUND_RETURN_OPTIONS + fc.FUND_MODES + ['plan']:
                info[fc.FUND_NAME] = info[fc.FUND_NAME].replace(rem, '')
    # add meta data
    if not info.get(fc.IS_OPEN_ENDED):
        info[fc.IS_OPEN_ENDED] = match.matchAnyIdentifier(fundType, ['open ended schemes'])
    if not info.get(fc.IS_DIRECT):
        info[fc.IS_DIRECT] = match.matchAnyIdentifier(fundName, ['direct'])
    if not info.get(fc.HAS_DIVIDEND):
        info[fc.HAS_DIVIDEND] = match.matchAnyIdentifier(fundName, ['dividend'])
    if info[fc.HAS_DIVIDEND] and not info.get(fc.DIVIDEND_PERIOD):
        periods = [fc.DIVIDEND_PERIOD_DAILY, fc.DIVIDEND_PERIOD_WEEKLY, fc.DIVIDEND_PERIOD_MONTHLY,\
                fc.DIVIDEND_PERIOD_SEMIANNUAL, fc.DIVIDEND_PERIOD_ANNUAL]
        info[fc.DIVIDEND_PERIOD] = match.matchOneIdentifier(fundName, periods)
    if not info.get(fc.ASSET_CLASS):
        if match.matchAnyIdentifier(fundType, ['balanced']):
            info[fc.ASSET_CLASS] = ac.ASSET_CLASS_HYBRID
        elif match.matchAnyIdentifier(fundType, fc.FUND_TYPES_DEBT) or \
            match.matchAnyIdentifier(fundName, fc.FUND_IDENTIFIERS_DEBT):
            info[fc.ASSET_CLASS] = ac.ASSET_CLASS_DEBT
        elif match.matchAnyIdentifier(fundType, fc.FUND_TYPES_EQUITY) or \
            match.matchAnyIdentifier(fundName, fc.FUND_IDENTIFIERS_EQUITY):
            info[fc.ASSET_CLASS] = ac.ASSET_CLASS_EQUITY
        else:
            info[fc.ASSET_CLASS] = '' # could not find anything
    # get the implied asset name from all parts. always recompute and replace
    parts = [
        info[fc.FUND_NAME],
        'dividend' if info[fc.HAS_DIVIDEND] else 'growth',
        'direct plan' if info[fc.IS_DIRECT] else 'regular plan',
    ]
    if len(info[fc.DIVIDEND_PERIOD]) > 0:
        parts[1] = info[fc.DIVIDEND_PERIOD] + ' ' + parts[1]
    info[ac.ASSET_NAME] = ' - '.join(parts).title()
    return info
