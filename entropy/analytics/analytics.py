'''returns and risk] analysis'''
import re
import pandas as pd
import numpy as np
import entropy.analytics.constants as ayc

# todo: rename to returnsAnalysis or equivalent
# todo: make unexposed functions private

def windowInDays(window):
    # todo: when window is period ('M'/'A')
    m = re.match(r'(\d+(\.\d+)?)([A-Z])', window)
    if not m:
        raise RuntimeError('Invalid window {}'.format(window))
    periods, freq = m.group(1, 3)
    return int(ayc.DAYS_IN_PERIOD[freq] * float(periods))

def annualizationFactor(df, window):
    if window == ayc.SINCE_INCEPTION:
        # todo: nullify
        lenWindow = df.expanding().count()
    else:
        # todo: return consistent type
        lenWindow = windowInDays(window)
    return ayc.DAYS_IN_PERIOD[ayc.YEAR] / lenWindow

# return in rolling window
def _return(df, periods):
    return df / df.fillna(method='ffill').shift(periods) - 1

def dailyReturn(df, initialVal=0):
    rtn = _return(df, 1).fillna(initialVal)
    rtn[df.isnull()] = np.nan
    return rtn

# move to test
def rollingReturn(df, window):
    return _return(df, windowInDays(window))

# move to test
def cumReturn(df, initialVal=0):
    return (1+dailyReturn(df, initialVal=initialVal)).cumprod() - 1

def transform(df, method, window):
    if method == ayc.AGG_ROLLING:
        if window == ayc.SINCE_INCEPTION:
            t = df.expanding()
        else:
            w = windowInDays(window)
            t = df.rolling(w, 1)
    elif method == ayc.AGG_PERIOD:
        # window here is actually period
        t = df.groupby(pd.TimeGrouper(window))
    elif method == ayc.AGG_LAST_PERIOD:
        t = df.last(window)
    elif method == ayc.AGG_LAST:
        # todo
        pass
    else:
        raise NotImplementedError("Unimplemented method {}".format(method))
    return t

def applyFunc(tfm, func, method):
    if method == ayc.AGG_ROLLING:
        df = tfm.apply(func)
    elif method == ayc.AGG_PERIOD:
        df = tfm.agg(func)
    elif method == ayc.AGG_LAST_PERIOD:
        df = tfm.apply(func, raw=True)
    else:
        raise NotImplementedError("Unimplemented method {}".format(method))
    return df

def aggReturn(df, method, window, annualize=False):
    aggR = applyFunc(transform(1 + df, method, window), ayc.METHOD[ayc.PROD], method) - 1
    # todo: window based logic is wrong for annualization
    # what about MTD?
    if annualize:
        aggR = pow(1 + aggR, annualizationFactor(df, window)) - 1
    return aggR

def mean(df, method, window, annualize=False):
    m = transform(df, method, window).mean() - 1
    if annualize:
        m = m * annualizationFactor(df, window)
    return m

def std(df, method, window, annualize=False):
    sd = transform(1 + df, method, window).std() - 1
    if annualize:
        sd = sd * np.sqrt(annualizationFactor(df, window))
    return sd

def var(df, method, window, annualize=False):
    v = transform(1 + df, method, window).var() - 1
    if annualize:
        v = v * annualizationFactor(df, window)
    return v
