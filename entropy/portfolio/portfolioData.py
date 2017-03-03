import hashlib
import datetime
import entropy.portfolio.constants as pc
from entropy.portfolio.portfolio import Portfolio
import entropy.utils.dateandtime as dtu
import entropy.utils.timeseries as tsu

def clientPortfolios(client, clientName):
    portCols = dict([(key, 1) for key in [pc.PORTFOLIO_ID, pc.PORTFOLIO_NAME, pc.DATE_CREATED]])
    data = client.portfolioData({pc.CLIENT_NAME : clientName}, portCols)
    if data.count() > 1:
        raise Exception('Found more than one portfolio for client {}'.format(clientName))
    return data[0]

# create/return unique portfolio ID based on portfolio and client name
def getPortfolioId(clientName, portfolioName):
    s = clientName + portfolioName
    Id = hashlib.md5(s.encode('utf-8'))
    return Id.hexdigest()

def newPortfolio(Id, clientName, portfolioName):
    now = dtu.localizeToTz(datetime.datetime.now())
    return({
        pc.PORTFOLIO_ID : Id,
        pc.CLIENT_NAME : clientName,
        pc.PORTFOLIO_NAME : portfolioName,
        pc.TRANSACTIONS : [],
        pc.DATE_CREATED : now
    })

def addPortfolio(client, clientName, portfolioName):
    Id = getPortfolioId(clientName, portfolioName)
    data = client.portfolioData({pc.PORTFOLIO_ID : Id})
    if data.count() > 0:
        raise 'Portfolio {} for {} already exists'.format(portfolioName, clientName)
    return client.addPortfolio(newPortfolio(Id, clientName, portfolioName))

def newTransactionId(transactions):
    if len(transactions) > 0:
        return max([T[pc.TRANSACTION_ID] for T in transactions]) + 1
    else:
        return 0

def newTransaction(Id, assetId, assetName, cashflow, quantity, date, txnType):
    return({
        pc.TRANSACTION_ID : Id,
        pc.ASSET_CODE : assetId,
        pc.ASSET_NAME : assetName,
        pc.TXN_CASHFLOW : cashflow,
        pc.TXN_QUANTITY : quantity,
        pc.TXN_DATE : date,
        pc.TXN_TYPE : txnType
    })

def addTransaction(client, portfolioId, assetId, schemeName, cashflow, quantity, date, txnType):
    Ts = Portfolio(portfolioId, client).transactions()
    transactionId = newTransactionId(Ts)
    Ts.append(newTransaction(transactionId, assetId, schemeName, cashflow, quantity, date, txnType))
    return client.updatePortfolio({pc.PORTFOLIO_ID : portfolioId}, {pc.TRANSACTIONS : Ts})

def addManyTransactions(client, portfolioId, txns):
    Ts = Portfolio(portfolioId, client).transactions()
    for txn in txns:
        txn[pc.TRANSACTION_ID] = newTransactionId(Ts)
        Ts.append(txn)
    return client.updatePortfolio({pc.PORTFOLIO_ID: portfolioId}, {pc.TRANSACTIONS : Ts})

def removeTransaction(client, portfolioId, transactionId):
    Ts = [txn for txn in Portfolio(portfolioId, client).transactions() \
    if txn.get(pc.TRANSACTION_ID) != transactionId]
    return client.updatePortfolio({pc.PORTFOLIO_ID : portfolioId}, {pc.TRANSACTIONS : Ts})

def removeAllTransactions(client, portfolioId):
    return client.updatePortfolio({pc.PORTFOLIO_ID : portfolioId}, {pc.TRANSACTIONS : []})
