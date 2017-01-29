import datetime
from entropy.db import dbclient
from entropy.utils import utils
import entropy.asset.constants as ac
from bson.objectid import ObjectId

def mongoIdFromId(Id):
    return ObjectId(Id)

def assetInfo(client, Ids, keys=[]):
    Ids = list(map(mongoIdFromId, Ids))
    projection = dict([(key, 1) for key in keys])
    data = [d for d in client.assetMetaData({dbclient.MONGO_ID: {"$in": Ids}}, projection)]
    if len(data) != len(Ids):
        raise "Could not find meta data for provided Ids"
    return data

# can be called by any asset after performing custom checks on updatedInfo
def updateAssetInfo(client, Id, updatedInfo={}):
    return client.updateAssetMetaData({dbclient.MONGO_ID: mongoIdFromId(Id)}, updatedInfo)

def valuesOnDate(client, dt):
    val = client.valueData({ac.VALUE_DATE : dt}, {dbclient.MONGO_ID : 0})
    if val.count() == 0:
        return {}
    elif val.count() > 1:
        raise "Found duplicate valuations for date: {}".format(dt.isoformat())
    return val[0]

def valuesByIds(client, Ids):
    keys = dict([(Id, 1) for Id in Ids])
    keys.update({ac.VALUE_DATE : 1, dbclient.MONGO_ID : 0})
    return [v for v in client.valueData({}, keys)]

def availableValueDates(client):
    return [dt[ac.VALUE_DATE] for dt in client.valueData({}, {ac.VALUE_DATE : 1, dbclient.MONGO_ID : 0})]

def updateValuesOnDate(client, dt, valueMap):
    valueMap[ac.VALUE_DATE] = utils.marketCloseFromDate(dt)
    ack = client.updateValueData({ac.VALUE_DATE : dt}, valueMap)
    return ack

def updateValuesByIds(client, Id, ts):
    pass
