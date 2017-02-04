from datetime import datetime
import io
import zipfile
import requests
from flask import jsonify
from flask.json import JSONEncoder
from bson.objectid import ObjectId
import pandas as pd
import entropy.utils.dateandtime as dtu

# ts2dict and dict2t
VALUES_KEY = "values"
DATES_KEY = "dates"

# all http responses will be of the form {data : <>}
JSON_KEY = "data"

def json(data):
    return jsonify({JSON_KEY : data})

def ts2dict(ts):
    ts = ts.dropna()
    # access and return the first column if there is only one
    vals = list(ts.values) if ts.columns.size > 1 else list(ts.iloc[:, 0].values)
    return({DATES_KEY: list(ts.index), VALUES_KEY: vals})

def dict2ts(dct):
    return pd.Series(dct[VALUES_KEY], index=dct[DATES_KEY])

def requestWithTries(url, params={}):
    counter = 3
    # retry 3 times to handle internet timeouts or network issues
    while counter > 0:
        try:
            resp = requests.get(url, params)
            counter = 0
        except Exception:
            counter = counter - 1
    return resp

def fileContentFromUrl(url, params={}):
    res = requestWithTries(url, params)
    return io.BytesIO(res.content)

def unzippedFileFromUrl(url, params={}):
    filename = fileContentFromUrl(url, params)
    return zipfile.ZipFile(filename)

# set this on the flask.json_encoder to encode dates in isoformat
class customJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                # python does not really conform to ISO 8601
                # it is not tz aware unless the TZ is explicitly set
                serial = dtu.localizeToTz(obj).isoformat()
                return serial
            elif isinstance(obj, ObjectId):
                serial = str(obj)
                return serial
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
