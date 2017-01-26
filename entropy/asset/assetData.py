import datetime
from entropy.db import dbclient
from entropy.utils import utils

VALUE_DATE = "valueDate"
ASSET_TYPE_KEY = 'assetType'

def valueDataOnDate(client, dt):
    val = client.valueData({VALUE_DATE : dt}, {dbclient.MONGO_ID : 0})
    if val.count() == 0:
        return {}
    elif val.count() > 1:
        raise "Found duplicate valuations for date: {}".format(dt.isoformat())
    return val[0]

def valuesById(client, _id):
    return client.valueData({}, { VALUE_DATE : 1, str(_id) : 1, dbclient.MONGO_ID : 0})

def availableValueDates(client):
    return [dt[VALUE_DATE] for dt in client.valueData({}, {VALUE_DATE : 1, dbclient.MONGO_ID : 0})]

def updateValueDataOnDate(client, dt, valueMap):
    valueMap[VALUE_DATE] = utils.marketCloseFromDate(dt)
    ack = client.updateValueData({VALUE_DATE : dt}, valueMap)
    return ack

def insertValuesForId(client, _id, ts):
    pass
