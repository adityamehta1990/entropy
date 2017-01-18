from pymongo import MongoClient
import datetime

MONGO_ID = "_id"

class MClient():
    """database client object"""
    def __init__(self):
        client = MongoClient()
        db = client.entropy_db
        self.fundDataColl = db.fund_data
        self.bmDataColl = db.bm_data
        self.portfolioDataColl = db.portfolio_data
        self.valueDataColl = db.value_data

    def fundData(self, filterCondition, keys={}):
        return self.fundDataColl.find(filterCondition, keys)

    def updateFundData(self, filterCondition, item):
        result = self.fundDataColl.update_one(filterCondition, {"$set" : item}, upsert=True)
        return result.acknowledged

    def valueDataOnDate(self, dt):
        val = self.valueDataColl.find({"valueDate":dt}, {MONGO_ID:0})
        if len(val) != 1:
            raise "Could not find valuation data on given date"
        return val

    def valueDataById(self, _id):
        return self.valueDataColl.find({}, {"valueDate": 1, str(_id): 1, MONGO_ID:0})

    def updateValueData(self, dt, valueMap):
        valueMap["valueDate"] = datetime.datetime(dt.year,dt.month,dt.day) # todo: define mkt close
        result = self.valueDataColl.update_one({"valueDate":dt}, {"$set":valueMap}, upsert=True)
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
