"""Constants for asset data"""
from entropy.db import dbclient

VALUE_DATE = 'valueDate'
ASSET_TYPE_KEY = 'assetType'
ASSET_CLASS = 'assetClass'
STRATEGY = 'strategy'
ASSET_NAME = 'assetName'
ASSET_ID = dbclient.MONGO_ID

ASSET_ATTRIBUTES = [ASSET_NAME, ASSET_CLASS, ASSET_TYPE_KEY, STRATEGY]

ASSET_CLASS_EQUITY = 'equity'
ASSET_CLASS_DEBT = 'debt'
ASSET_CLASS_HYBRID = 'hybrid'
