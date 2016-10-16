import pandas as pd
import constants

# only perform manipulations on data
# should take raw inputs, should not know about db

def periodReturn( ts, period ):
    pass

def rollingReturn( ts, window ):
    windowInDays = constants.NUMDAYS[ window ]
    ts = ts.resample('D').pad() # ensure curve is daily by padding with last value
    return( ts.pct_change(windowInDays) )
