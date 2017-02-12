"""Constants for analytics"""

import entropy.constants as ec
import entropy.config as config
import numpy as np

# same as pandas frequency constants
DAY = 'D'
WEEK = 'W'
MONTH = 'M'
QUARTER = 'Q'
YEAR = 'A'

SINCE_INCEPTION = 'SI'

DAYS_IN_PERIOD = {
    ec.CALENDAR_EVERYDAY : {
        DAY : 1,
        WEEK : 7,
        MONTH : 30,
        QUARTER : 120,
        YEAR : 365
    },
    ec.CALENDAR_WEEKDAY : {
        DAY : 1,
        WEEK : 5,
        MONTH : 21,
        QUARTER : 63,
        YEAR : 252,
    }
}[config.CALENDAR]

SUM = "sum"
PROD = "product"
MIN = "minumum"
MAX = "maximum"
AVG = "average"
STD = "standard deviation"
VAR = "variance"
CORR = "correlation"
COV = "covariance"
MSUM = "multiplicative sum"

METHOD = {
    SUM : np.nansum,
    PROD : np.nanprod,
    AVG : np.nanmean,
    VAR : np.nanvar,
    STD : np.nanstd,
    MIN : np.nanmin,
    MAX : np.nanmax,
}