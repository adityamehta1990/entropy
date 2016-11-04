import pandas as pd
import re
import numpy as np
import scipy
import scipy.optimize
import constants

# timeseries analysis of returns

DAYS_IN_YEAR = 365
PERIOD_TO_DAYS = {
    'D' : 1,
    'W' : 7,
    'M' : 30,
    'Q' : 90,
    'Y' : 365
}

# 3Y -> ('Y',3)
def parseWindow(window):
    for freq in PERIOD_TO_DAYS.keys():
        if window.endswith(freq):
            periods = int(window.replace(freq,''))
            break
    else:
        raise Exception( 'Unknown frequency in window {}'.format(window) )
    return (freq,periods)

# return in rolling window
def rollingReturn(nav,window):
    (freq,periods) = parseWindow( window )
    windowInDays = PERIOD_TO_DAYS[ freq ] * periods
    nav = nav.resample('D').pad() # ensure curve is daily by padding with last value
    return nav.pct_change(windowInDays) # leave NAs as is

# t in years (>=1)
def annualize(ret,t):
    if t < 1:
        raise Exception( 'Should not annualize returns for less than a year' )
    return pow(1 + ret,1/t) - 1

# cum return from start to end of series
def cumReturn(ret):
    ts = ret + 1
    ret = ts.cumprod().values[-1] - 1
    t = ( ts.last_valid_index() -  ts.first_valid_index() ).days / DAYS_IN_YEAR
    if t >= 1:
        ret = annualize(ret,t)
    return ret

# period from today such as 3y return
def periodReturn(returns,window):
    (freq,periods) = parseWindow(window)
    numDays = PERIOD_TO_DAYS[freq] * periods
    if returns.size < numDays:
        return None
    ret = cumReturn( returns.tail(numDays) )
    return ret

# returns by calendar year/month
def calendarPeriodReturns(returns,type='month'):
    ts = returns + 1
    if type == 'month':
        grps = ts.groupby(pd.TimeGrouper('M'))
    elif type == 'year':
        grps = ts.groupby(pd.TimeGrouper('A'))
    else:
        raise Exception('Unrecognized calendar period {}'.format(type))
    # todo: label by year/month and partial period
    return grps.agg({
        'start': lambda x: x.first_valid_index(),
        'end': lambda x: x.last_valid_index(),
        'returns': lambda x: np.prod(x)
    }).reset_index().drop('index',1) # remove index
