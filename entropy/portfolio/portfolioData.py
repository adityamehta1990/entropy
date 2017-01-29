import hashlib
import datetime
import entropy.portfolio.constants as pc
from entropy.portfolio.portfolio import Portfolio
from entropy.utils import utils

def clientPortfolios(client, clientName):
    portCols = dict([(key, 1) for key in [pc.PORTFOLIO_ID, pc.PORTFOLIO_NAME, pc.DATE_CREATED]])
    data = client.portfolioData({pc.CLIENT_NAME : clientName}, portCols)
    return [scheme for scheme in data]

# create/return unique portfolio ID based on portfolio and client name
def portfolioId(clientName, portfolioName):
    s = clientName + portfolioName
    Id = hashlib.md5(s.encode('utf-8'))
    return Id.hexdigest()

def newPortfolio(Id, clientName, portfolioName):
    now = utils.localizeToIST(datetime.datetime.today())
    return({
        pc.PORTFOLIO_ID : Id,
        pc.CLIENT_NAME : clientName,
        pc.PORTFOLIO_NAME : portfolioName,
        pc.TRANSACTIONS : [],
        pc.DATE_CREATED : now
    })

def addPortfolio(client, clientName, portfolioName):
    Id = portfolioId(clientName, portfolioName)
    data = client.portfolioData({pc.PORTFOLIO_ID : Id})
    if data.count() > 0:
        return False
    return client.addPortfolio(newPortfolio(Id, clientName, portfolioName))

def newTransactionId(transactions):
    if len(transactions) > 0:
        return max([T[pc.TRANSACTION_ID] for T in transactions]) + 1
    else:
        return 0

def newTransaction(Id, assetId, schemeName, cashflow, quantity, date):
    return({
        pc.TRANSACTION_ID : Id,
        pc.ASSET_CODE : assetId,
        pc.ASSET_NAME : schemeName,
        pc.TXN_CASHFLOW : cashflow,
        pc.TXN_QUANTITY : quantity,
        pc.TXN_DATE : date
    })

def addTransaction(client, portfolioId, assetId, schemeName, cashflow, quantity, date):
    Ts = Portfolio(portfolioId, client).transactions()
    transactionId = newTransactionId(Ts)
    Ts.append(newTransaction(transactionId, assetId, schemeName, cashflow, quantity, date))
    return client.updatePortfolio({pc.PORTFOLIO_ID : portfolioId}, {pc.TRANSACTIONS : Ts})

def removeTransaction(client, portfolioId, transactionId):
    Ts = [txn for txn in Portfolio(portfolioId, client).transactions() if txn.get(pc.TRANSACTION_ID) != transactionId]
    return client.updatePortfolio({pc.PORTFOLIO_ID : portfolioId}, {pc.TRANSACTIONS : Ts})

def removeAllTransactions(client, portfolioId):
    return client.updatePortfolio({pc.PORTFOLIO_ID : portfolioId}, {pc.TRANSACTIONS : []})
