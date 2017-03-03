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
    if data.count() != 1:
        raise "Invalid amfi code {}".format(amfiCode)
    return str(data[0][dbclient.MONGO_ID])

def fundIdFromFundName(client, fundName):
    info = enrichFundInfo({fc.FUND_NAME_AMFI: fundName})
    funds = fundList(client)
    fund = match.matchDictBest(info, funds, key=ac.ASSET_NAME)
    return fund.get(dbclient.MONGO_ID)

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
    '''for use in fuzzywuzzy or other fund name processing
    removes separators and unimportant parts of name such as option or plan
    '''
    pattern = re.compile('option|plan', re.IGNORECASE)
    fundName = pattern.sub('', fundName)
    fundName = re.sub('standard', 'Regular', fundName, flags=re.IGNORECASE)
    if not match.matchAnyIdentifier(fundName, [fc.DIVIDEND_PERIOD_SEMIANNUAL]):
        fundName = re.sub('yearly', fc.DIVIDEND_PERIOD_ANNUAL, fundName, re.IGNORECASE)
    fundName = ' '.join(fundName.replace('-', ' ').split())
    return fundName.strip()

def fundClassification(fundName, fundType):
    '''classify asset class and strategy'''
    # todo: classify strategy/substrategy
    info = {}
    if match.matchAnyIdentifier(fundType, fc.FUND_TYPES_HYBRID) or \
        match.matchAnyIdentifier(fundName, fc.FUND_IDENTIFIERS_HYBRID):
        info[fc.ASSET_CLASS] = ac.ASSET_CLASS_HYBRID
    elif match.matchAnyIdentifier(fundType, fc.FUND_TYPES_DEBT) or \
        match.matchAnyIdentifier(fundName, fc.FUND_IDENTIFIERS_DEBT):
        info[fc.ASSET_CLASS] = ac.ASSET_CLASS_DEBT
    elif match.matchAnyIdentifier(fundType, fc.FUND_TYPES_EQUITY) or \
        match.matchAnyIdentifier(fundName, fc.FUND_IDENTIFIERS_EQUITY):
        info[fc.ASSET_CLASS] = ac.ASSET_CLASS_EQUITY
    else:
        info[fc.ASSET_CLASS] = '' # could not find anything
    return info

# only enrich missing data
def enrichFundInfo(info, forceEnrich=False):
    '''parse fund name, type etc to get various meta data
    set forceEnrich to True to replace existing meta data passed in info
    '''
    fundName = fundNameProcessor(info.get(fc.FUND_NAME_AMFI, ''))
    fundType = info.get(fc.FUND_TYPE, '').lower()
    # classify asset class, strategy, etc
    newInfo = fundClassification(fundName, fundType)
    # fund base name - strip out growth/div and direct plan info
    pattern = re.compile('|'.join(fc.FUND_RETURN_OPTIONS + fc.FUND_MODES + \
                    fc.DIVIDEND_PERIODS + ['plan', 'div']), re.IGNORECASE)
    newInfo[fc.FUND_NAME] = pattern.sub('', fundName).strip()
    # add meta data
    fundName = fundName.lower() # dont lower for FUND_NAME
    newInfo[fc.IS_OPEN_ENDED] = match.matchAnyIdentifier(fundType, ['open ended schemes'])
    newInfo[fc.IS_DIRECT] = match.matchAnyIdentifier(fundName, ['direct'])
    newInfo[fc.HAS_DIVIDEND] = match.matchAnyIdentifier(fundName, ['dividend', 'div'])
    if newInfo[fc.HAS_DIVIDEND]:
        newInfo[fc.DIVIDEND_PERIOD] = match.matchOneIdentifier(fundName, fc.DIVIDEND_PERIODS)
    if forceEnrich:
        info.update(newInfo)
    else:
        newInfo.update(info) # copy back old values from info and reassign
        info = newInfo
    # get the implied asset name from all parts. always recompute and replace
    parts = [info[fc.FUND_NAME]]
    if info[fc.HAS_DIVIDEND]:
        parts.append(((info[fc.DIVIDEND_PERIOD] or '').title() + ' Dividend').strip())
    else:
        parts.append('Growth')
    parts.append('Direct' if info[fc.IS_DIRECT] else 'Regular')
    info[ac.ASSET_NAME] = ' - '.join(parts)
    return info
