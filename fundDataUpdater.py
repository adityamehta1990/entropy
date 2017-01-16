from entropy.datafeeds import fundDataFeed
from entropy.db import dbclient

client = dbclient.MClient()

funds = fundDataFeed.fundDataFromAMFI()
res = client.fundDataColl.insert_many(funds)

# daily
fundDataFeed.updateDailyFundNAV(client)
# historical
fundDataFeed.updateHistFundNAV(client)
