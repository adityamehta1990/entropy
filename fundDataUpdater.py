from entropy.datafeeds import fundDataFeed
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu

client = dbclient.MClient()
# update meta data
fundDataFeed.updateFundMetaData(client)
# daily
fundDataFeed.updateDailyFundNAV(client)
# historical
# fundDataFeed.updateHistFundNAV(client) # for full history
fundDataFeed.updateHistFundNAV(client, startDate=dtu.dateParser('20140401'))
