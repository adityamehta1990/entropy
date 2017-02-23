"""Constants for asset data"""
from entropy.db import dbclient

VALUE_DATE = 'valueDate'
ASSET_TYPE_KEY = 'assetType'
ASSET_CLASS = 'assetClass'
STRATEGY = 'strategy'
ASSET_NAME = 'assetName'
ASSET_ID = dbclient.MONGO_ID

ASSET_ATTRIBUTES = [ASSET_NAME, ASSET_CLASS, ASSET_TYPE_KEY, STRATEGY]

# asset classes and associated keys
ASSET_CLASS_EQUITY = 'equity'
ASSET_CLASS_DEBT = 'debt'
ASSET_CLASS_HYBRID = 'hybrid'

# common
SECTOR = 'sector'

# equity
MARKET_CAP = 'marketCap' # mega, large, mid, small, micro
STYLE = 'style' # value, growth, blend

# debt
CREDIT_QUALITY = 'creditQuality' # high, medium, low
DURATION = 'duration' # long, medium, short
UNDERLIER_TYPE = 'underlierType' # gilt, corp, money market
