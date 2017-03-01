from entropy.db import dbclient
import entropy.portfolio.portfolioData as po
import entropy.portfolio.constants as pc
import entropy.fund.constants as fc
import entropy.utils.dateandtime as dtu
import datetime
import entropy.fund.fundData as fundData
from entropy.fund.fund import Fund
from entropy.portfolio.portfolio import Portfolio
import pandas as pd

client = dbclient.MClient()
date = dtu.dateParser('20150101')
fundList = fundData.fundList(client)

# adding new portfolio, if it doesn't exist
clientName = 'Warren Buffet'
if len(po.clientPortfolios(client, clientName)) == 0:
    po.addPortfolio(client, clientName, "my Life's Savings")
Id = po.clientPortfolios(client, clientName)[0][pc.PORTFOLIO_ID]

Txns = [
    [ "date",       "hour", "schemeCode",   "cashFlow"  ],
    [ "20160405",   5,      "125494",       1e4         ],
    [ "20160601",   7,      "100356",       2e4         ],
    [ "20160601",   13,     "118991",       3e3         ],
    [ "20160701",   7,      "101042",       4e3         ],
    [ "20160701",   11,     "100356",       6e4         ],
    [ "20160901",   14,     "113566",       4e4         ],
    [ "20160901",   15,     "113566",       1e4         ],
    #[ "20160105",   5,      "118991",       9e4         ],
    #[ "20160105",   8,      "125494",       -3e3        ],
    #[ "20160105",   10,     "118991",       7e3         ],
]

Txns = pd.DataFrame(Txns[1:],columns=Txns[0])

for txn in Txns.itertuples():
    fund = Fund(fundData.fundIdFromAmfiCode(client,txn.schemeCode),client)
    txnDate = dtu.parse(txn.date)
    nav = fund.nav().loc[dtu.nextMarketClose(txnDate)][fund.Id]
    po.addTransaction( \
        client, Id, fund.Id, fund.fundInfo()[fc.FUND_NAME_AMFI], \
        txn.cashFlow, txn.cashFlow / nav, txnDate + datetime.timedelta(hours=int(txn.hour)) \
     )

# P = Portfolio(Id = Id,client=client)
# P.transactions()