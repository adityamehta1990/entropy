from pymongo import MongoClient
import datetime

MONGO_ID = "_id"

class MClient():
    """database client object"""
    def __init__(self):
        client = MongoClient()
        db = client.entropy_db
        self.assetMetaDataColl = db.asset_meta_data
        self.portfolioDataColl = db.portfolio_data
        self.valueDataColl = db.value_data

    def assetMetaData(self, filterCondition, keys={}):
        return self.assetMetaDataColl.find(filterCondition, keys)

    def updateAssetMetaData(self, filterCondition, item):
        result = self.assetMetaDataColl.update_one(filterCondition, {"$set" : item}, upsert=True)
        return result.acknowledged

    def valueData(self, filterCondition, keys={}):
        return self.valueDataColl.find(filterCondition, keys)

    def updateValueData(self, filterCondition, valueMap):
        result = self.valueDataColl.update_one(filterCondition, {"$set" : valueMap}, upsert=True)
        return result.acknowledged

    def portfolioData(self, filterCondition, keys={}):
        keys[MONGO_ID] = 0
        return self.portfolioDataColl.find(filterCondition, keys)

    def addPortfolio(self, item):
        result = self.portfolioDataColl.insert_one(item)     # todo: dateCreated
        return result.acknowledged

    def updatePortfolio(self, filterCondition, item):
        result = self.portfolioDataColl.update_one(filterCondition, {"$set" : item})   # todo: lastUpdated
        return result.acknowledged
