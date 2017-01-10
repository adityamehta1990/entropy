from pymongo import MongoClient

MONGO_ID = "_id"

class MClient():
    """database client object"""
    def __init__(self):
        client = MongoClient()
        db = client.fund_db
        self.fundDataColl = db.fund_data
        self.bmDataColl = db.bm_data
        self.portfolioDataColl = db.portfolio_data
        self.valueDataColl = db.value_data

    def fundData(self, filterCondition, keys={}):
        keys[MONGO_ID] = 0 # we never care about mongo id
        return self.fundDataColl.find(filterCondition, keys)

    def updateFundData(self, filterCondition, item):
        result = self.fundDataColl.update_one(filterCondition, {"$set" : item})
        return result.acknowledged

    def portfolioData(self, filterCondition, keys={}):
        keys[MONGO_ID] = 0
        return self.portfolioDataColl.find(filterCondition, keys)

    def addPortfolio(self, item):
        result = self.portfolioDataColl.insert_one(item);     # todo: dateCreated
        return result.acknowledged

    def updatePortfolio(self, filterCondition, item):
        result = self.portfolioDataColl.update_one(filterCondition, {"$set" : item})   # todo: lastUpdated
        return result.acknowledged;
