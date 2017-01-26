from flask import jsonify
from flask.json import JSONEncoder
from datetime import datetime
from bson.objectid import ObjectId
from dateutil.parser import parse
from pytz import timezone
import pandas as pd

# todo: Compartmentalize this into different scripts

# all http responses will be of the form {data : <>}
JSON_KEY = "data"

# ts2dict and dict2ts
VALUES_KEY = "values"
DATES_KEY = "dates"

# market close hour
MARKET_CLOSE_HOUR = 14

def localizeToIST(dt):
    ist = timezone('Asia/Kolkata')
    return ist.localize(dt)

def addToDate(date,deltaInDays):
    return date + datetime.timedelta(days=deltaInDays)
    return date + datetime.timedelta(days=deltaInDays)

# parse ISO date string to datetime
def dateParser(dateStr):
    return parse(dateStr)

def marketCloseFromDate(dt):
    return datetime(dt.year, dt.month, dt.day, MARKET_CLOSE_HOUR);

# todo: implement
def dailyClose(df):
    pass

# todo: implement
def dailySum(df):
    pass

# regular week dates
def periodicDates(startDate,endDate=datetime.today()):
    start = marketCloseFromDate(startDate)
    end = marketCloseFromDate(endDate)
    dates = pd.DatetimeIndex(freq='D', start=start, end=end)
    return [ d for d in dates if d.weekday() < 5 ] # Num Weekday: Monday = 0, Sunday = 6
    
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
            elif isinstance(obj, ObjectId):
                serial = str(obj)
                return serial
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)