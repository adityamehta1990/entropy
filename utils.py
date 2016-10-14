from flask import jsonify
from flask.json import JSONEncoder
import calendar
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import pytz
import constants
import pandas as pd

ist = timezone('Asia/Kolkata')

# parse ISO date string to datetime
def dateParser(dateStr):
    return parse(dateStr);

def json( data ):
    return( jsonify( { constants.JSON_KEY : data } ) )

def ts2dict( ts ):
    ts = ts.dropna();
    return( { constants.DATES_KEY : list( ts.index ), constants.VALUES_KEY : list( ts.values ) });

def dict2ts( dict ):
    return( pd.Series( dict[ constants.VALUES_KEY ], index=dict[ constants.DATES_KEY ] ) );

# set this on the flask.json_encoder to encode dates in isoformat
class customJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                # python does not really conform to ISO 8601
                # it is not tz aware unless the TZ is explicitly set
                serial = ist.localize(obj).isoformat()
                return serial
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
