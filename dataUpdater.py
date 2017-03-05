'''Run this script to fill/update asset data
DO NOT import this script!
'''
import argparse
from entropy.datafeeds import bseFeeds
from entropy.datafeeds import nseFeeds
from entropy.datafeeds import amfiFeeds
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu

parser = argparse.ArgumentParser(description=\
    'Fill meta data and value data for funds, stocks and benchmarks.' +
    'By default, values are pulled for unfilled historical dates.')
parser.add_argument('--verbose', help='Print verbose logs', action='store_true')
parser.add_argument('--redo', help='Set/Update values for dates starting today', action='store_true')
parser.add_argument('--enrich', help='Enrich and overwrite fund meta data', action='store_true')
parser.add_argument('--mindate', help='Date upto which values will be filled', default='20160401')
args = parser.parse_args()

client = dbclient.MClient()
verbose = args.verbose
redo = args.redo
startDate = dtu.dateParser(args.mindate)
forceEnrich = args.enrich

print('Running dataUpdater...')
print('Using args: verbose={}, redo={}, startDate={}, forceEnrich={}'.format(verbose, redo, startDate, forceEnrich))

# update meta data
failedFunds = amfiFeeds.updateFundMetaData(client, forceEnrich=forceEnrich)
# daily
amfiFeeds.updateDailyFundNAV(client)
# historical
failedFundDates = amfiFeeds.updateHistFundNAV(client, startDate=startDate, verbose=verbose, redo=redo)

failedStocks = bseFeeds.updateStockMetaData(client, filename='data/ListOfScripsEquity.csv')
bseFeeds.updateDailyStockPrices(client)
failedStockDates = bseFeeds.updateHistStockPrices(client, startDate=startDate, verbose=verbose, redo=redo)

failedBMs = nseFeeds.updateBenchmarkMetaData(client)
nseFeeds.updateDailyBenchmarkPrices(client)
failedBMDates = nseFeeds.updateHistBenchmarkPrices(client, startDate=startDate, verbose=verbose, redo=redo)
