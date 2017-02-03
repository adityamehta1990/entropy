import entropy.utils.dateandtime as dtu
import numpy as np

def alignToRegularDates(df, method=None):
    if len(df) == 0:
        return df
    return df.reindex(index=dtu.regularDates(df.index[0], df.index[-1]), method=method)

def dropInitialNa(df):
    return df[df.first_valid_index():]

def _lastNonNa(arr):
    ind = np.where(~np.isnan(arr))[0]
    if len(ind) == 0:
        return np.NaN
    else:
        return arr[ind[-1]]

def _dailyAgg(df, aggFunc):
    df['nextMarketClose'] = df.apply(lambda r: dtu.nextMarketClose(r.name), axis=1)
    df = df.groupby('nextMarketClose').aggregate(aggFunc)
    df.index.name = None
    return df

def dailyClose(df):
    return _dailyAgg(df, _lastNonNa)

def dailySum(df):
    return _dailyAgg(df, np.sum)
