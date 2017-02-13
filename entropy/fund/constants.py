import entropy.asset.constants as ac
# define schema, possible values, etc

# database schema
# from amfi
FUND_NAME_AMFI = "fundNameRaw"
FUND_CODE_AMFI = "amfiCode"
FUND_HOUSE = "fundHouse"
FUND_TYPE = "fundType"
ISIN = "ISIN"
ASSET_TYPE_KEY = ac.ASSET_TYPE_KEY # hardcoded because it is always a fund
# calculated by string parsing or input
FUND_NAME = "fundName" # nicer looking fund name
ASSET_CLASS = "assetClass"
STRATEGY_TYPE = "strategyType" # this is a short hand for investment attributes
IS_OPEN_ENDED = 'isOpenEnded'
HAS_DIVIDEND = 'hasDividend'
DIVIDEND_PERIOD = 'hasDividend'
IS_DIRECT = 'isDirect'

FUND_ATTRIBUTES = ac.ASSET_ATTRIBUTES + \
                [FUND_NAME_AMFI, FUND_CODE_AMFI, FUND_HOUSE, FUND_TYPE, ISIN, \
                FUND_NAME, IS_OPEN_ENDED, HAS_DIVIDEND, DIVIDEND_PERIOD, IS_DIRECT]

# allowed values
ASSET_TYPE_FUND = "fund"

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

FUND_TYPE_CHOICES = ["open ended schemes", "close ended schemes", "interval fund schemes"]
FUND_RETURN_OPTIONS = ['growth', 'dividend']
FUND_INVESTMENT_OPTIONS = ['direct', 'regular']
