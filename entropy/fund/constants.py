'''Fund Constants'''
import entropy.asset.constants as ac
import entropy.analytics.constants as ayc
# define schema, possible values, etc

# database schema
# from amfi
FUND_NAME_AMFI = 'fundNameRaw'
FUND_CODE_AMFI = 'amfiCode'
FUND_HOUSE = 'fundHouse'
FUND_TYPE = 'fundType'
ISIN = 'ISIN'
ASSET_TYPE_KEY = ac.ASSET_TYPE_KEY # hardcoded because it is always a fund
# calculated by string parsing or input
FUND_NAME = 'fundName'
ASSET_CLASS = 'assetClass'
STRATEGY_TYPE = 'strategyType' # this is a short hand for investment attributes
IS_OPEN_ENDED = 'isOpenEnded'
HAS_DIVIDEND = 'hasDividend'
DIVIDEND_PERIOD = 'divPeriod'
IS_DIRECT = 'isDirect'

FUND_ATTRIBUTES = ac.ASSET_ATTRIBUTES + \
                [FUND_NAME_AMFI, FUND_CODE_AMFI, FUND_HOUSE, FUND_TYPE, ISIN, \
                FUND_NAME, IS_OPEN_ENDED, HAS_DIVIDEND, DIVIDEND_PERIOD, IS_DIRECT]

# allowed values
ASSET_TYPE_FUND = 'fund'

FUND_TYPE_CHOICES = ['open ended schemes', 'close ended schemes', 'interval fund schemes']
FUND_TYPES_HYBRID = ['balanced', 'fund of funds']
FUND_TYPES_DEBT = ['income', 'liquid', 'gilt', 'money market', 'floating rate']
FUND_TYPES_EQUITY = ['elss', 'other etfs']

# FUND_IDENTIFIERS_<x> refer to parts of fund name that can help identify <x>
FUND_IDENTIFIERS_HYBRID = ['arbitrage']
FUND_IDENTIFIERS_DEBT = ['monthly income', 'short term', 'medium term', 'credit', 'gilt', 'corporate']
FUND_IDENTIFIERS_EQUITY = ['equity', 'equities', 'large cap', 'midcap', 'small cap', 'mid cap',\
        'bluechip', 'blue chip', 'top 100', 'top 200', 'index fund']

# todo: incorporate below to assign further classification
LARGE_CAP_IDENTIFIERS = ['large cap', 'bluechip', 'blue chip', 'top 100', 'top 200']
MID_CAP_IDENTIFIERS = ['midcap', 'mid cap']
SMALL_CAP_IDENTIFIERS = ['small cap']

FUND_RETURN_OPTIONS = ['growth', 'dividend']
FUND_MODES = ['direct', 'regular']

DIVIDEND_PERIOD_DAILY = 'daily'
DIVIDEND_PERIOD_WEEKLY = 'weekly'
DIVIDEND_PERIOD_MONTHLY = 'monthly'
DIVIDEND_PERIOD_SEMIANNUAL = 'half yearly'
DIVIDEND_PERIOD_ANNUAL = 'yearly'
DIVIDEND_PERIODS = [DIVIDEND_PERIOD_DAILY, DIVIDEND_PERIOD_WEEKLY, DIVIDEND_PERIOD_MONTHLY,\
                DIVIDEND_PERIOD_SEMIANNUAL, DIVIDEND_PERIOD_ANNUAL]
