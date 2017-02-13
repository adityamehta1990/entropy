from entropy.db import dbclient
import entropy.utils.dateandtime as dtu
import entropy.asset.constants as ac
from bson.objectid import ObjectId

def mongoIdFromId(Id):
    return ObjectId(Id)

def assetList(client, assetType=None, keys=ac.ASSET_ATTRIBUTES, navDate=None):
    query = {ac.ASSET_TYPE_KEY: assetType} if assetType is not None else {}
    projection = dict([(key, 1) for key in keys])
    assets = [a for a in client.assetMetaData(query, projection)]
    if navDate is not None:
        vals = valuesOnDate(client, navDate)
        assets = [a for a in assets if vals.get(str(a[dbclient.MONGO_ID])) is not None]
    return assets

def assetInfo(client, Ids, keys=ac.ASSET_ATTRIBUTES):
    if isinstance(Ids, str):
        Ids = [Ids]
    Ids = [mongoIdFromId(Id) for Id in Ids]
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

def updateValuesOnDate(client, dt, valueMap, assetType, assetKey):
    assetCodeMap = client.assetMetaData({ac.ASSET_TYPE_KEY: assetType}, {assetKey:1})
    dt = dtu.marketCloseFromDate(dt)
    newValueMap = {}
    for asset in assetCodeMap:
        if valueMap.get(asset[assetKey]) is not None:
            newValueMap[str(asset[dbclient.MONGO_ID])] = valueMap[asset[assetKey]]
    newValueMap[ac.VALUE_DATE] = dt
    ack = client.updateValueData({ac.VALUE_DATE: dt}, newValueMap)
    return ack

def updateValuesByIds(client, Id, ts):
    pass
