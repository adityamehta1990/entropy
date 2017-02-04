"""Constants for analytics"""

import entropy.constants as ec
import entropy.config as config

DAY = 'D'
WEEK = 'W'
MONTH = 'M'
QUARTER = 'Q'
YEAR = 'D'

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