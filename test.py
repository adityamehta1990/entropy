from entropy.db import dbclient
import entropy.portfolio.portfolioData as po
from entropy.portfolio.constants import *
import entropy.utils.utils as utils
import datetime
import entropy.fund.fundData as fundData
from entropy.portfolio.portfolio import Portfolio
import pandas as pd

client = dbclient.MClient()
date = utils.dateParser('20150101');
fundList = fundData.fundList(client)

# adding new portfolio, if it doesn't exist
clientName = 'Warren Buffet'
if( len(po.clientPortfolios(client,clientName)) == 0 ):
    po.addPortfolio(client, clientName, "my Life's Savings")
Id = po.clientPortfolios(client,clientName)[0][PORTFOLIO_ID]

Txns = [
    [ "date",       "hour", "schemeCode",   "cashFlow"  ],
    [ "20150105",   5,      "125494",       1e4         ],
    [ "20150301",   7,      "100356",       2e4         ],
    [ "20150601",   13,     "118991",       3e3         ],
    [ "20150701",   7,      "101042",       4e3         ],
    [ "20150701",   11,     "100356",       6e4         ],
    [ "20150901",   14,     "113566",       4e4         ],
    [ "20150901",   15,     "113566",       1e4         ],
    [ "20160105",   5,      "118991",       9e4         ],
    [ "20160105",   8,      "125494",       -3e3        ],
    [ "20160105",   10,     "118991",       7e3         ],
];

Txns = pd.DataFrame(Txns[1:],columns=Txns[0])

for txn in Txns.itertuples():
    fund = Fund(fundIdFromAmfiCode(client,txn.schemeCode),client)
    po.addTransaction( \
        client, Id, fund.Id, fund.fundInfo()[fundData.FUND_NAME_AMFI], \
        txn.cashFlow, 0, utils.parse(txn.date) + datetime.timedelta(hours=txn.hour) \
     )

# P = Portfolio(client=client, portfolioId = Id)
# P.transactions()