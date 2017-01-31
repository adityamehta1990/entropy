from flask import jsonify
from flask.json import JSONEncoder
from datetime import datetime
from datetime import timedelta
from bson.objectid import ObjectId
from dateutil.parser import parse
from pytz import timezone
import pandas as pd
import numpy as np

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

def lastNonNa(a):
    ind = np.where(~np.isnan(a))[0]
    if len(ind) == 0:
        return np.NaN
    else:
        return a[ind[-1]]

# parse ISO date string to datetime
def dateParser(dateStr):
    return parse(dateStr)

def marketCloseFromDate(dt):
    return datetime(dt.year, dt.month, dt.day, MARKET_CLOSE_HOUR);

def nextMarketClose(dt):
    close = marketCloseFromDate(dt)
    if dt <= close:
        nextClose = close
    else:
        nextClose = close + timedelta(days=1)
    # Note: ( max( dt.weekday(), 4 ) - 4 ) gives the same as following
    if nextClose.weekday() >= 5:
        weekdayAdj = 7 - nextClose.weekday()
    else:
        weekdayAdj = 0
    return nextClose + timedelta(days=weekdayAdj)

# regular week dates
def regularDates(startDate,endDate=datetime.today()):
    start = marketCloseFromDate(startDate)
    end = marketCloseFromDate(endDate)
    dates = pd.DatetimeIndex(freq='D', start=start, end=end)
    return [ d for d in dates if d.weekday() < 5 ] # Num Weekday: Monday = 0, Sunday = 6

def alignToRegularDates(df,method=None):
    if len(df) == 0:
        return df
    return df.reindex(index=regularDates(df.index[0],df.index[-1]),method=method)

def dropInitialNa(df):
    return df[df.first_valid_index():]

# todo: implement
def _dailyAgg(df,aggFunc):
    df['nextMarketClose'] = df.apply(lambda r: nextMarketClose(r.name), axis=1)
    df = df.groupby('nextMarketClose').aggregate(aggFunc)
    df.index.name = None
    return df

def dailyClose(df):
    return _dailyAgg(df,lastNonNa)

def dailySum(df):
    return _dailyAgg(df,np.sum)
    
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
