from datetime import datetime
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
    return({DATES_KEY : list(ts.index), VALUES_KEY : list(ts.values)})

def dict2ts(dct):
    return pd.Series(dct[VALUES_KEY], index=dct[DATES_KEY])

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


