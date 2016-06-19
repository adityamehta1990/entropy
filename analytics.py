import dbio
import pandas as pd
import constants

def ts2dict( ts ):
    return( { constants.DATES_KEY : list( ts.index ), constants.VALUES_KEY : list( ts.values ) });

def dict2ts( ts ):
    return( pd.Series( ts[ constants.VALUES_KEY ], index=ts[ constants.DATES_KEY ] ) );

def tsreturn( ts, window ):
    windowInDays = constants.NUMDAYS[ window ];
    # todo: align to daily
    return( (ts/ts.shift(windowInDays)) - 1 );

def fundReturn( client, schemeCode, window ):
    nav = dict2ts( dbio.fundNav( client, schemeCode ) );
    return ts2dict( tsreturn( nav, window ) );
