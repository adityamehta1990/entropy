# Unorganized test fns
import numpy as np
import pandas as pd
from datetime import timedelta
import entropy.utils.dateandtime as dtu
import entropy.utils.timeseries as tsu
import entropy.utils.webio as webio

def dfFromTable(Table):
    header = Table[0]
    df = pd.DataFrame(Table[1:])
    df.columns = Table[0]
    df.index = df.apply(lambda row: dtu.dateParser(row['Date']) + timedelta(hours=row['Hour']), axis=1)
    return df[[c for c in df.columns if c != 'Date' and c != 'Hour']]

# Test for daily close
E = np.NaN
T1 = [
    [ "Date",       "Hour", "Value 1",  "Value 2"   ],
    [ "20170127",   5,      3,          E           ],
    [ "20170127",   11,     E,          E           ],
    [ "20170127",   13,     4,          E           ],
    [ "20170127",   19,     E,          5           ],
    [ "20170128",   5,      3,          9           ],
    [ "20170129",   17,     E,          4           ],
    [ "20170130",   12,     4,          E           ],
    [ "20170202",   7,      E,          5           ],
    [ "20170202",   9,      E,          3           ],
    [ "20170202",   22,     4,          7           ],
    [ "20170203",   15,     E,          5           ],
]

T2 = [
    [ "Date",       "Hour", "Value 1",  "Value 2"   ],
    [ "20170127",   14,      7,          E           ],
    [ "20170130",   14,      7,          18          ],
    [ "20170131",   14,      E,          E           ],
    [ "20170201",   14,      E,          E           ],
    [ "20170202",   14,      E,          8           ],
    [ "20170203",   14,      4,          7           ],
    [ "20170206",   14,      E,          5           ],
]

df1 = dfFromTable(T1)
df2 = dfFromTable(T2)
df3 = tsu.alignToRegularDates(tsu.dailySum(df1))

assert df3.equals(df2)
assert df1.equals(webio.dict2ts(webio.ts2dict(df1)))

# Test basic functionality

T1 = [
    [ "Date",       "Hour", "Value 2",  "Value 1",   "Value 3", ],
    [ "20170101",   2,      E,          E,           E,         ],
    [ "20170101",   5,      E,          E,           2,         ],
    [ "20170102",   0,      7,          E,           3,         ],
    [ "20170103",   0,      1,          3,           1,         ],
    [ "20170104",   0,      3,          E,           6,         ],
]

T2 = [
    [ "Date",       "Hour", "Value 1",  "Value 2",   ],
    [ "20170101",   0,      3,          4            ],
    [ "20170102",   0,      1,          1,           ],
    [ "20170103",   0,      3,          E            ],
    [ "20170104",   0,      3,          E            ],
]

df1 = dfFromTable(T1)
df2 = dfFromTable(T2)
