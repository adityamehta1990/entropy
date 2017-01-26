import hashlib
import datetime
from constants import *
from portfolio import Portfolio
from entropy.utils import utils

def clientPortfolios(client, clientName):
    schemeCols = dict([(key, 1) for key in [PORTFOLIO_ID, PORTFOLIO_NAME, DATE_CREATED]])
    data = client.portfolioData({CLIENT_NAME : clientName}, schemeCols)
    return [scheme for scheme in data]

# create/return unique portfolio ID based on portfolio and client name
def portfolioId(clientName, portfolioName):
    s = clientName + portfolioName
    Id = hashlib.md5(s.encode('utf-8'))
    return Id.hexdigest()

def newPortfolio(Id, clientName, portfolioName):
    now = utils.localizeToIST(datetime.datetime.today())
    return({
        PORTFOLIO_ID : Id,
        CLIENT_NAME : clientName,
        PORTFOLIO_NAME : portfolioName,
        TRANSACTIONS : [],
        DATE_CREATED : now
    })

def addPortfolio(client, clientName, portfolioName):
    Id = portfolioId(clientName, portfolioName)
    data = client.portfolioData({PORTFOLIO_ID : Id})
    if(data.count() > 0):
        return False
    return(client.addPortfolio(newPortfolio(Id, clientName, portfolioName)))

def newTransactionId(transactions):
    if len(transactions) > 0:
        return max([T[TRANSACTION_ID] for T in transactions]) + 1
    else:
        return 0

def newTransaction(Id, schemeCode, schemeName, cashflow, quantity, date):
    return({
        TRANSACTION_ID : Id,
        ASSET_CODE : schemeCode,
        ASSET_NAME : schemeName,
        TXN_CASHFLOW : cashflow,
        TXN_QUANTITY : quantity,
        TXN_DATE : date
    })

def addTransaction(client, portfolioId, schemeCode, schemeName, cashflow, quantity, date):
    Ts = Portfolio(portfolioId, client).transactions()
    transactionId = newTransactionId(Ts)
    Ts.append(newTransaction(transactionId, schemeCode, schemeName, cashflow, quantity, date))
    return client.updatePortfolio({PORTFOLIO_ID : portfolioId}, {TRANSACTIONS : Ts })

def removeTransaction(client, portfolioId, transactionId):
    Ts = [txn for txn in Portfolio(portfolioId,client).transactions() if txn.get(TRANSACTION_ID) != transactionId]
    return client.updatePortfolio({PORTFOLIO_ID : portfolioId}, {TRANSACTIONS : Ts})

def removeAllTransactions(client, portfolioId):
    return client.updatePortfolio({PORTFOLIO_ID : portfolioId}, {TRANSACTIONS : []})