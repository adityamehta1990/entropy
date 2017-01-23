from flask import jsonify
from flask.json import JSONEncoder
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import pandas as pd

# all http responses will be of the form {data : <>}
JSON_KEY = "data"

# ts2dict and dict2ts
VALUES_KEY = "values"
DATES_KEY = "dates"

def localizeToIST(dt):
    ist = timezone('Asia/Kolkata')
    return ist.localize(dt)

# parse ISO date string to datetime
def dateParser(dateStr):
    return parse(dateStr)

def json( data ):
    return( jsonify( { JSON_KEY : data } ) )

def ts2dict( ts ):
    ts = ts.dropna()
    return( { DATES_KEY : list( ts.index ), VALUES_KEY : list( ts.values ) })

def dict2ts( dict ):
    return( pd.Series( dict[ VALUES_KEY ], index=dict[ DATES_KEY ] ) )

# set this on the flask.json_encoder to encode dates in isoformat
class customJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                # python does not really conform to ISO 8601
                # it is not tz aware unless the TZ is explicitly set
                serial = localizeToIST(obj).isoformat()
                return serial
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
