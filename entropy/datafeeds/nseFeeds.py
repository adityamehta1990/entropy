'''Index data feeds from NSE'''
import datetime
import pandas as pd
from entropy.asset import assetData
import entropy.utils.dateandtime as dtu
import entropy.utils.webio as webio
import entropy.asset.constants as ac
import entropy.benchmark.constants as bmc

# equity list with ISIN and industry. this is independent of provider
# simply download the csv (top right), save and run <>
# http://www.bseindia.com/corporates/List_Scrips.aspx?expandable=1%3fexpandable%3d1

# stock and index data from NSE
# https://www.nseindia.com/content/indices/ind_close_all_25012017.csv
# https://www.nseindia.com/archives/equities/bhavcopy/pr/PR250117.zip

NSE_INDEX_LEVEL_URL = "https://www.nseindia.com/content/indices/ind_close_all_"
NSE_DAILY_DATA_URL = "https://www.nseindia.com/archives/equities/bhavcopy/pr/PR"

def benchmarkMetaData(filename):
    df = pd.read_csv(filename)
    # strip string columns
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    df[ac.ASSET_TYPE_KEY] = bmc.ASSET_TYPE_BENCHMARK
    df[ac.ASSET_NAME] = df[bmc.BENCHMARK_NAME]
    df = df.fillna('')
    return df.to_dict('records')

def updateBenchmarkMetaData(client, filename='data/benchmarkMetaData.csv'):
    bmInfoArray = benchmarkMetaData(filename)
    missing = []
    for bmi in bmInfoArray:
        # checkWrongKeys(bmi, bmc.BENCHMARK_ATTRIBUTES)
        bmName = bmi.get(bmc.BENCHMARK_NAME)
        if bmName:
            ack = client.updateAssetMetaData({bmc.BENCHMARK_NAME: bmName}, bmi)
            if not ack:
                missing.append(bmName)
    return ack

def bmLevelsFromNSE(dt):
    dtStr = dt.strftime("%d%m%Y")
    url = NSE_INDEX_LEVEL_URL + dtStr + ".csv"
    csv = webio.fileContentFromUrl(url)
    df = pd.read_csv(csv)
    valueMap = dict(zip(df['Index Name'], df['Closing Index Value']))
    return valueMap

# unused
def dailyDataFromNSE(dt):
    dtStr = dt.strftime("%d%m%y")
    url = NSE_DAILY_DATA_URL + dtStr + ".zip"
    unzip = webio.unzippedFileFromUrl(url)
    filename = "Pd" + dtStr + ".csv"
    csv = unzip.open(filename)
    df = pd.read_csv(csv, skipinitialspace=True)
    # data = unzip.read(filename).splitlines()
    # indexVals = df[lambda x: x.MKT == 'Y']
    # valueMap = dict(zip(indexVals.SECURITY, indexVals.CLOSE_PRICE))
    return df

# unused
def updateStockVals(client, dt, df):
    '''get values for stocks and update'''
    stockVals = df[lambda x: x.SERIES == 'EQ']
    stockVals = stockVals.dropna(subset=['SYMBOL'])
    valueMap = dict(zip(stockVals.SYMBOL, stockVals.CLOSE_PRICE))
    return assetData.updateValuesOnDate(client, dt, valueMap, "stock", "ticker")

def updateBMVals(client, dt, valueMap):
    return assetData.updateValuesOnDate(client, dt, valueMap, bmc.ASSET_TYPE_BENCHMARK, bmc.BENCHMARK_NAME)

def updateDailyBenchmarkPrices(client):
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    try:
        valueMap = bmLevelsFromNSE(dt)
        ack = updateBMVals(client, dt, valueMap)
    except Exception:
        print("Skipping for %s"%(dt.date()))
        ack = False
    return ack

def updateHistBenchmarkPrices(client, startDate=dtu.dateParser('20060401'), verbose=False, redo=False):
    filledDts = assetData.availableValueDates(client)
    dt = datetime.datetime.today() - datetime.timedelta(days=2) if redo else min(filledDts)
    missing = []
    while dt >= startDate:
        try:
            valueMap = bmLevelsFromNSE(dt)
            ack = updateBMVals(client, dt, valueMap)
            if not ack:
                print('Failed to write db for %s'%(dt.date()))
            elif verbose:
                print("Update successful for %s"%(dt.date()))
        except Exception:
            missing.append(dt)
            print("Skipping for %s"%(dt.date()))
        dt = dtu.prevMarketClose(dt - datetime.timedelta(days=1))
    return missing
