import datetime
from entropy.db import dbclient
from entropy.utils import utils

VALUE_DATE = "valueDate"
ASSET_TYPE_KEY = 'assetType'

def assetInfoById(client, mongoId, keys=[]):
    projection = dict([(key, 1) for key in keys])
    data = client.assetMetaData({dbclient.MONGO_ID: mongoId}, projection)
    if data.count() == 1:
        data = data[0]
    else:
        raise "Could not find data for Id: " + str(mongoId)
    return data

def assetInfoByIds(client, mongoIds, keys=[]):
    projection = dict([(key, 1) for key in keys])
    data = [d for d in client.assetMetaData({dbclient.MONGO_ID: {"$in": mongoIds}}, projection)]
    if len(data) != len(mongoIds):
        raise "Could not find meta data for provided Ids"
    return data

def valueDataOnDate(client, dt):
    val = client.valueData({VALUE_DATE : dt}, {dbclient.MONGO_ID : 0})
    if val.count() == 0:
        return {}
    elif val.count() > 1:
        raise "Found duplicate valuations for date: {}".format(dt.isoformat())
    return val[0]

def valuesById(client, Id):
    return [v for v in client.valueData({}, {VALUE_DATE: 1, Id: 1, dbclient.MONGO_ID: 0})]

def valuesByIds(client, Ids):
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
