import pandas as pd
import re
import numpy as np
import entropy.analytics.constants as ac

# 3.5Y -> (3.5,'Y')
def windowInDays(window):
    m = re.match(r'(\d+(\.\d+)?)([A-Z])', window)
    assert m, 'Invalid window'
    periods, freq = m.group(1, 3)
    return int(ac.DAYS_IN_PERIOD[freq] * float(periods))

def annualizationFactor(window):
    return ac.DAYS_IN_PERIOD[ac.YEAR] / window

# return in rolling window
def _return(df, periods):
    return df / df.fillna(method='ffill').shift(periods) - 1

def dailyReturn(df, initialVal=0):
    rtn = _return(df, 1).fillna(initialVal)
    rtn[df.isnull()] = np.nan
    return rtn

def rollingReturn(df, window):
    return _return(df, windowInDays(window))

def cumReturn(df, initialVal=0):
    return (1+dailyReturn(df, initialVal=initialVal)).cumprod() - 1

# better implementation (performance optimization):
# individual stats as functions and rolling/period/last_period as method_args
def rollingStat(df, window, stat, annualize=True):
    return df.rolling(windowInDays(window)).apply(ac.METHOD[stat])

def periodStat(df, period, stat, annualize=True):
    return df.groupby(pd.TimeGrouper(period)).agg(ac.METHOD[stat])

def lastPeriodStat(df, period, stat, annualize=True):
    return df.last(period).apply(ac.METHOD[stat], raw=True)
