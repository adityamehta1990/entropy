import datetime
from entropy.db import dbclient
from entropy.utils import utils
from bson.objectid import ObjectId

VALUE_DATE = "valueDate"
ASSET_TYPE_KEY = 'assetType'

# todo: all the functions here take mongoIds and not Ids
#       either pass Ids or change function names

def mongoIdFromId(Id):
    return ObjectId(Id)

def assetInfo(client, Ids, keys=[]):
    Ids = map(mongoIdFromId,Ids)
    projection = dict([(key, 1) for key in keys])
    data = [d for d in client.assetMetaData({dbclient.MONGO_ID: {"$in": Ids}}, projection)]
    if len(data) != len(Ids):
        raise "Could not find meta data for provided Ids"
    return data

def valueDataOnDate(client, dt):
    val = client.valueData({VALUE_DATE : dt}, {dbclient.MONGO_ID : 0})
    if val.count() == 0:
        return {}
    elif val.count() > 1:
        raise "Found duplicate valuations for date: {}".format(dt.isoformat())
    return val[0]

def values(client, Ids):
    keys = dict([(Id, 1) for Id in Ids])
    keys.update({VALUE_DATE : 1, dbclient.MONGO_ID : 0})
    return [v for v in client.valueData({}, keys)]

def availableValueDates(client):
    return [dt[VALUE_DATE] for dt in client.valueData({}, {VALUE_DATE : 1, dbclient.MONGO_ID : 0})]

def updateValueDataOnDate(client, dt, valueMap):
    valueMap[VALUE_DATE] = utils.marketCloseFromDate(dt)
    ack = client.updateValueData({VALUE_DATE : dt}, valueMap)
    return ack

def insertValuesForId(client, Id, ts):
    pass
