"""Constants for asset data"""
from entropy.db import dbclient

VALUE_DATE = 'valueDate'
ASSET_TYPE_KEY = 'assetType'
ASSET_CLASS = 'assetClass'
ASSET_NAME = 'assetName'
ASSET_ID = dbclient.MONGO_ID

ASSET_ATTRIBUTES = [ASSET_NAME, ASSET_CLASS, ASSET_TYPE_KEY]
