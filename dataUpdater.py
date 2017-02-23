'''Run this script to fill/update asset data
DO NOT import this script!
'''
from entropy.datafeeds import bseFeeds
from entropy.datafeeds import nseFeeds
from entropy.datafeeds import amfiFeeds
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu

client = dbclient.MClient()
verbose = True
startDate = dtu.dateParser('20140401')

# update meta data
failedFunds = amfiFeeds.updateFundMetaData(client, forceEnrich=False)
# daily
amfiFeeds.updateDailyFundNAV(client)
# historical
failedFundDates = amfiFeeds.updateHistFundNAV(client, startDate=startDate, verbose=verbose)

failedStocks = bseFeeds.updateStockMetaData(client, filename='data/ListOfScripsEquity.csv')
bseFeeds.updateDailyStockPrices(client)
failedStockDates = bseFeeds.updateHistStockPrices(client, startDate=startDate, verbose=verbose)

failedBMs = nseFeeds.updateBenchmarkMetaData(client)
nseFeeds.updateDailyBenchmarkPrices(client)
failedBMDates = nseFeeds.updateHistBenchmarkPrices(client, startDate=startDate, verbose=verbose)
