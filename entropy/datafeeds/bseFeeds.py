'''Stock and bond data feeds from BSE'''
import datetime
import pandas as pd
from entropy.asset import assetData
import entropy.asset.constants as ac
import entropy.stock.constants as sc
import entropy.bond.constants as bc
import entropy.utils.webio as webio
import entropy.utils.dateandtime as dtu

# equity list with ISIN and industry. this is independent of provider
# download the csv (button on top right), save/update ListOfScrips<type>.csv
# run updateStockMetaData
# http://www.bseindia.com/corporates/List_Scrips.aspx?expandable=1%3fexpandable%3d1
# http://www.bseindia.com/download/BhavCopy/Equity/EQ310117_CSV.ZIP
# http://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_310117.zip
# http://www.bseindia.com/download/Bhavcopy/Debt/DEBTBHAVCOPY31012017.zip

BSE_STOCK_DATA_URL = "http://www.bseindia.com/download/BhavCopy/Equity/EQ"
BSE_BOND_DATA_URL = "http://www.bseindia.com/download/Bhavcopy/Debt/DEBTBHAVCOPY"

BSE_COLUMN_NAMES = ['Security Code', 'Security Id', 'Security Name', 'Status', \
                'Group', 'Face Value', 'ISIN No', 'Industry']
STOCK_KEYS = [sc.STOCK_CODE_BSE, sc.TICKER, sc.STOCK_NAME, sc.STOCK_STATUS, \
            sc.STOCK_GROUP, sc.FACE_VALUE, sc.ISIN, sc.INDUSTRY]
BOND_KEYS = [bc.BOND_CODE_BSE, bc.TICKER, bc.BOND_NAME, bc.BOND_STATUS, \
            bc.BOND_GROUP, bc.FACE_VALUE, bc.ISIN, bc.INDUSTRY]

# todo: the same for bonds, with its own constants
def readAssetMetaData(filename, assetClass='equity'):
    df = pd.read_csv(filename)
    # strip string columns
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    # asset type/class, and rename columns by type
    df[ac.ASSET_CLASS] = assetClass
    if assetClass == 'equity':
        df[ac.ASSET_TYPE_KEY] = sc.ASSET_TYPE_STOCK
        assetColumnNames = STOCK_KEYS
    elif assetClass == 'debt':
        df[ac.ASSET_TYPE_KEY] = bc.ASSET_TYPE_BOND
        assetColumnNames = BOND_KEYS
    else:
        raise 'Unknown asset class'
    renameMap = dict(zip(BSE_COLUMN_NAMES, assetColumnNames))
    df = df.rename(columns=renameMap)
    df[ac.ASSET_NAME] = df[sc.STOCK_NAME]
    df = df.drop('Instrument', 1)
    return df.to_dict('records')

def updateStockMetaData(client, filename='data/ListOfScripsEquity.csv'):
    stockInfoArray = readAssetMetaData(filename, 'equity')
    missing = []
    for si in stockInfoArray:
        # stockData.checkStockAttributes(si)
        bseCode = si.get(sc.STOCK_CODE_BSE)
        if bseCode:
            ack = client.updateAssetMetaData({sc.STOCK_CODE_BSE: bseCode}, si)
            if not ack:
                missing.append(bseCode)
    return missing

def updateBondMetaData(client, filename='data/ListOfScripsBond.csv'):
    bondInfoArray = readAssetMetaData(filename, 'debt')
    ack = True
    for bi in bondInfoArray:
        # stockData.checkStockttributes(fi)
        bseCode = bi.get(bc.BOND_CODE_BSE)
        if bseCode:
            ack = client.updateAssetMetaData({bc.BOND_CODE_BSE: bseCode}, bi) and ack
    return ack

def stockPricesFromBSE(dt):
    dtStr = dt.strftime("%d%m%y")
    url = BSE_STOCK_DATA_URL + dtStr + "_CSV.zip"
    unzip = webio.unzippedFileFromUrl(url)
    filename = "EQ" + dtStr + ".CSV"
    csv = unzip.open(filename)
    df = pd.read_csv(csv, skipinitialspace=True)
    # SC_CODE is bseCode
    # todo: floating point error due to machine precision
    valueMap = dict(zip(df.SC_CODE, df.CLOSE))
    return valueMap

# there is more to bonds than prices in the data from bse
# lets worry about this later, because bonds are unlikely holdings
def bondPricesFromBSE(dt):
    dtStr = dt.strftime("%d%m%Y")
    url = BSE_BOND_DATA_URL + dtStr + ".zip"
    unzip = webio.unzippedFileFromUrl(url)
    # todo: iterate over all files in zip (different types of bonds/debentures)
    filename = "fgroup" + dtStr + ".csv"
    csv = unzip.open(filename)
    df = pd.read_csv(csv, skipinitialspace=True)
    # todo: floating point error due to machine precision
    valueMap = dict(zip(df.SC_CODE, df.CLOSE))
    return valueMap

def updateStockPrices(client, dt, valueMap):
    return assetData.updateValuesOnDate(client, dt, valueMap, sc.ASSET_TYPE_STOCK, sc.STOCK_CODE_BSE)

def updateDailyStockPrices(client):
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    try:
        prices = stockPricesFromBSE(dt)
        ack = updateStockPrices(client, dt, prices)
    except Exception:
        print("Skipping for %s"%(dt.date()))
        ack = False
    return ack

# todo: centralize error handling
def updateHistStockPrices(client, startDate=dtu.dateParser('20060401'), verbose=False):
    dt = datetime.datetime.today() - datetime.timedelta(days=2)
    missing = []
    while dt >= startDate:
        # try catch due to holidays - remove after implementing holiday calendar
        try:
            prices = stockPricesFromBSE(dt)
            ack = updateStockPrices(client, dt, prices)
            if not ack:
                print('Failed to write db for %s'%(dt.date()))
            elif verbose:
                print("Update successful for %s"%(dt.date()))
        except Exception:
            missing.append(dt)
            print("Skipping for %s"%(dt.date()))
        dt = dtu.prevMarketClose(dt - datetime.timedelta(days=1))
    return missing
