from entropy.datafeeds import fundDataFeed
from entropy.db import dbclient
import entropy.utils.utils as utils

client = dbclient.MClient()
funds = fundDataFeed.fundDataFromAMFI()
res = client.fundDataColl.insert_many(funds)

# daily
fundDataFeed.updateDailyFundNAV(client)
# historical
# fundDataFeed.updateHistFundNAV(client)
fundDataFeed.updateHistFundNAV(client,startDate=utils.dateParser('20140401'))
