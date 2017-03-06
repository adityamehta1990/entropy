'''Run this script to fill/update asset data
DO NOT import this script!
'''
import argparse
import datetime
from entropy.asset import assetData
from entropy.datafeeds import bseFeeds
from entropy.datafeeds import nseFeeds
from entropy.datafeeds import amfiFeeds
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu

client = dbclient.MClient()

filledDts = assetData.availableValueDates(client)
maxDt = min(filledDts)
minDt = maxDt - datetime.timedelta(days=365)

parser = argparse.ArgumentParser(description=\
    'Fill meta data and value data for funds, stocks and benchmarks.' +
    'By default, values are pulled for unfilled historical dates.')
parser.add_argument('--verbose', help='Print verbose logs', action='store_true')
parser.add_argument('--enrich', help='Enrich and overwrite fund meta data', action='store_true')
parser.add_argument('--mindate', help='Date until which values will be filled', default=minDt.strftime('%Y%m%d'))
parser.add_argument('--maxdate', help='Date before which values will be filled', default=maxDt.strftime('%Y%m%d'))
args = parser.parse_args()

verbose = args.verbose
minDt = dtu.dateParser(args.mindate)
maxDt = dtu.dateParser(args.maxdate)
forceEnrich = args.enrich

print('Running dataUpdater...')
print('Using args: verbose={}, dateRange=({}, {}), forceEnrich={}'.format(\
    verbose, minDt.strftime('%Y%m%d'), maxDt.strftime('%Y%m%d'), forceEnrich))

# update meta data
failedFunds = amfiFeeds.updateFundMetaData(client, forceEnrich=forceEnrich)
# daily
amfiFeeds.updateDailyFundNAV(client)
# historical
failedFundDates = amfiFeeds.updateHistFundNAV(client, minDate=minDt, maxDate=maxDt, verbose=verbose)
print('Filled fund NAVs, failed for {} dates'.format(len(failedFundDates)))

failedStocks = bseFeeds.updateStockMetaData(client, filename='data/ListOfScripsEquity.csv')
bseFeeds.updateDailyStockPrices(client)
failedStockDates = bseFeeds.updateHistStockPrices(client, minDate=minDt, maxDate=maxDt, verbose=verbose)
print('Filled stock prices, failed for {} dates'.format(len(failedStockDates)))

failedBMs = nseFeeds.updateBenchmarkMetaData(client)
nseFeeds.updateDailyBenchmarkPrices(client)
failedBMDates = nseFeeds.updateHistBenchmarkPrices(client, minDate=minDt, maxDate=maxDt, verbose=verbose)
print('Filled BM levels, failed for {} dates'.format(len(failedBMDates)))
