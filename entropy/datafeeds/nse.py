import requests
import pandas as pd
import zipfile
import io
import datetime
from entropy.asset import assetData
import entropy.utils.dateandtime as dtu

# equity list with ISIN and industry. this is independent of provider
# simply download the csv (top right), save and run <>
# http://www.bseindia.com/corporates/List_Scrips.aspx?expandable=1%3fexpandable%3d1

# stock and index data from NSE
# https://www.nseindia.com/content/indices/ind_close_all_25012017.csv
# https://www.nseindia.com/archives/equities/bhavcopy/pr/PR250117.zip

NSE_INDEX_LEVEL_URL = "https://www.nseindia.com/content/indices/ind_close_all_"
NSE_DAILY_DATA_URL = "https://www.nseindia.com/archives/equities/bhavcopy/pr/PR"

def bmLevelsFromNSE():
    csv = requests.get(NSE_INDEX_LEVEL_URL).content
    data = pd.read_csv(csv)

def dailyDataFromNSE(dt):
    dtStr = dt.strftime("%d%m%y")
    url = NSE_DAILY_DATA_URL + dtStr + ".zip"
    res = requests.get(url)
    unzip = zipfile.ZipFile(io.BytesIO(res.content))
    filename = "Pd" + dtStr + ".csv"
    csv = unzip.open(filename)
    df = pd.read_csv(csv, skipinitialspace=True)
    # data = unzip.read(filename).splitlines()
    return df

def updateBMVals(client, dt, df):
    indexVals = df[lambda x: x.MKT == 'Y']
    valueMap = dict(zip(indexVals.SECURITY, indexVals.CLOSE_PRICE))
    return assetData.updateValuesOnDate(client, dt, valueMap, "benchmark", "bmName")

def updateStockVals(client, dt, df):
    '''get values for stocks and update'''
    stockVals = df[lambda x: x.SERIES == 'EQ']
    stockVals = stockVals.dropna(subset=['SYMBOL'])
    valueMap = dict(zip(stockVals.SYMBOL, stockVals.CLOSE_PRICE))
    return assetData.updateValuesOnDate(client, dt, valueMap, "stock", "ticker")

def updateHistDataFromNSE(client, startDate=dtu.dateParser('20060401')):
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    ack = True
    while dt != startDate:
        df = dailyDataFromNSE(dt)
        ack = updateBMVals(client, dt, df) and ack
        ack = updateStockVals(client, dt, df) and ack
        if ack:
            print("Update successful for %s"%(dt.date()))
        dt = dt - datetime.timedelta(days=1)
    return ack
