'''run this script to fill data'''
from entropy.datafeeds import bseFeeds
from entropy.datafeeds import nseFeeds
from entropy.datafeeds import amfiFeeds
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu

client = dbclient.MClient()

# update meta data
amfiFeeds.updateFundMetaData(client)
# daily
amfiFeeds.updateDailyFundNAV(client)
# historical
# fundDataFeed.updateHistFundNAV(client) # for full history
amfiFeeds.updateHistFundNAV(client, startDate=dtu.dateParser('20140401'))

bseFeeds.updateStockMetaData(client, filename='data/ListOfScripsEquity.csv')
bseFeeds.updateDailyStockPrices(client)
bseFeeds.updateHistStockPrices(client, startDate=dtu.dateParser('20140401'))

nseFeeds.updateBenchmarkMetaData(client)
nseFeeds.updateDailyBenchmarkPrices(client)
nseFeeds.updateHistBenchmarkPrices(client, startDate=dtu.dateParser('20140401'))
