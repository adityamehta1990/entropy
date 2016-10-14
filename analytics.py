import pandas as pd
import constants

# only perform manipulations on data
# should take raw inputs, should not know about db

def tsreturn( ts, window ):
    windowInDays = constants.NUMDAYS[ window ];
    # todo: align to daily
    return( (ts/ts.shift(windowInDays)) - 1 );
