import re
import datetime
from entropy.fund import fundData
import entropy.fund.constants as fc
import entropy.utils.webio as webio
import entropy.utils.dateandtime as dtu

AMFI_DAILY_NAV_URL = 'http://portal.amfiindia.com/spages/NAV0.txt'
# http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=53&tp=1&frmdt=02-Jan-2017&todt=03-Jan-2017
# frmdt, todt, mf (fund house code), tp (fund type)
AMFI_HIST_NAV_URL = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx'

def fundNAVFromAMFI(dt=datetime.datetime.today() - datetime.timedelta(days=1)):
    dtStr = dt.strftime('%d-%b-%Y')
    # compare date because we dont care about exact time
    if dt.date() == datetime.datetime.today().date() - datetime.timedelta(days=1):
        resp = webio.requestWithTries(AMFI_DAILY_NAV_URL)
    else:
        resp = webio.requestWithTries(AMFI_HIST_NAV_URL, {'frmdt':dtStr})
    data = resp.text.splitlines()
    data = [line.strip().split(';') for line in data if line.find(';') >= 0 and line.endswith(dtStr)]
    # potentially use schema = data[0].split(';') to figure out below indexes
    # schemeCodeIdx = 0
    # NAVIdx = 4
    valueMap = [(line[0], float(line[4].replace(',', ''))) for line in data if line[4] != 'N.A.']
    return dict(valueMap)

# todo: write fund class and data to make sure parsed data conforms
def fundDataFromAMFI(forceEnrich=False):
    # it looks like this has all funds that were ever sold
    # so need to call it only first time and when we want to update with new funds
    resp = webio.requestWithTries(AMFI_DAILY_NAV_URL)
    data = resp.text.splitlines()
    # schema = data[0].split(';') # schema is on the first line
    data = [line.strip() for line in data[1:] if len(line.strip()) > 0]
    fundList = []
    pattern = re.compile('|'.join(fc.FUND_TYPE_CHOICES), re.IGNORECASE)
    currFundType = currFundHouse = ""
    for line in data:
        if line.find(';') >= 0:
            parts = line.split(';')
            info = {
                fc.FUND_HOUSE : currFundHouse,
                fc.FUND_TYPE : currFundType,
                fc.FUND_CODE_AMFI : parts[0],
                fc.FUND_NAME_AMFI : parts[3],
                fc.ISIN : parts[1],
                fc.ASSET_TYPE_KEY : fc.ASSET_TYPE_FUND
            }
            info = fundData.enrichFundInfo(info, forceUpdate=forceEnrich)
            fundList.append(info)
        else:
            if pattern.search(line) is not None:
                currFundType = line
            else:
                currFundHouse = line
    return fundList

def updateFundMetaData(client, forceEnrich=False):
    fundInfoArray = fundDataFromAMFI(forceEnrich=forceEnrich)
    missing = []
    for fi in fundInfoArray:
        fundData.checkFundAttributes(fi)
        amfiCode = fi.get(fc.FUND_CODE_AMFI)
        if amfiCode:
            ack = client.updateAssetMetaData({fc.FUND_CODE_AMFI: amfiCode}, fi)
            if not ack:
                missing.append(amfiCode)
    return missing

# this should be called separately from the server (without concurrent dbclients preferably)
def updateDailyFundNAV(client):
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    valueMap = fundNAVFromAMFI(dt)
    ack = fundData.updateFundNAVOnDate(client, dt, valueMap)
    if not ack:
        print('Failed to write db for %s'%(dt.date()))
    return ack

# this is a one time thing
# amfi has data from 1st Apr 2006
def updateHistFundNAV(client, startDate=dtu.dateParser('20060401'), verbose=False):
    # todo: check min updated date and use that
    # this will just refill everything
    dt = datetime.datetime.today() - datetime.timedelta(days=2)
    missing = []
    while dt >= startDate:
        try:
            valueMap = fundNAVFromAMFI(dt)
            ack = fundData.updateFundNAVOnDate(client, dt, valueMap)
            if not ack:
                print('Failed to write db for %s'%(dt.date()))
            elif verbose:
                print("Update successful for %s"%(dt.date()))
        except Exception:
            missing.append(dt)
            print("Skipping for %s"%(dt.date()))
        dt = dt - datetime.timedelta(days=1)
    return missing
