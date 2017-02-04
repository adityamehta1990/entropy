from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from pytz import timezone
import pandas as pd
import numpy as np
import entropy.config as config

# todo: calendar
# todo: timezone

# market close hour
MARKET_CLOSE_HOUR = 14

def localizeToTz(dt):
    tz = timezone(config.TIME_ZONE)
    return tz.localize(dt)

# parse ISO date string to datetime
def dateParser(dateStr):
    return parse(dateStr)

def marketCloseFromDate(dt):
    return datetime(dt.year, dt.month, dt.day, MARKET_CLOSE_HOUR)

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

def prevMarketClose(dt):
    close = marketCloseFromDate(dt)
    if dt >= close:
        prevClose = close
    else:
        prevClose = close - timedelta(days=1)
    if prevClose.weekday() >= 5:
        weekdayAdj = prevClose.weekday() - 4
    else:
        weekdayAdj = 0
    return prevClose - timedelta(days=weekdayAdj)

# regular week dates
def regularDates(startDate, endDate=datetime.today()):
    start = marketCloseFromDate(startDate)
    end = marketCloseFromDate(endDate)
    dates = pd.DatetimeIndex(freq='D', start=start, end=end)
    return [d for d in dates if d.weekday() < 5] # Num Weekday: Monday = 0, Sunday = 6
