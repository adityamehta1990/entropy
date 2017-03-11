'''Routes for portfolio data'''
from flask import Blueprint
from flask import request
from entropy.db import dbclient
import entropy.utils.dateandtime as dtu
import entropy.utils.webio as webio
from entropy.portfolio import portfolioData
from entropy.portfolio.portfolio import Portfolio
from entropy.portfolio import txnUpload
import entropy.portfolio.constants as pc

portfolio_api = Blueprint('portfolio_api', __name__)
client = dbclient.MClient()

@portfolio_api.route('/client/<clientName>')
def getClientPortfolio(clientName):
    return webio.json(portfolioData.getClientPortfolio(client, clientName))

@portfolio_api.route('/<portfolioId>')
def getPortfolioData(portfolioId):
    return webio.json(Portfolio(portfolioId, client).portfolioData())

@portfolio_api.route('/new', methods=['POST'])
def addPortfolio():
    clientName = request[pc.CLIENT_NAME].strip()
    portfolioName = request[pc.PORTFOLIO_NAME].strip()
    portfolioId = portfolioData.addPortfolio(client, clientName, portfolioName)
    return webio.json(portfolioId)

@portfolio_api.route('/<portfolioId>/transactions')
def getPortfolioTransactions(portfolioId):
    return webio.json(Portfolio(portfolioId, client).transactions())

@portfolio_api.route('/<portfolioId>/transactions/upload', methods=['POST'])
def uploadTransactions(portfolioId):
    file = webio.getUploadedFile()
    failed = txnUpload.importFundTransactionsFromFile(client, portfolioId, file)
    return webio.json(failed)

@portfolio_api.route('/<portfolioId>/transaction/new', methods=['POST'])
def addTransaction(portfolioId):
    data = request.get_json()
    ack = portfolioData.addTransaction(
        client, portfolioId, data[pc.ASSET_CODE],
        data[pc.ASSET_NAME], data[portfolioData.TXN_CASHFLOW],
        data[pc.TXN_QUANTITY], dtu.dateParser(data[pc.TXN_DATE]),
        data.get(pc.TXN_TYPE))
    return webio.json(ack)

@portfolio_api.route('/<portfolioId>/transaction/<transactionId>', methods=['DELETE'])
def removeTransaction(portfolioId, transactionId):
    # todo: add elif for PUT (Modify)
    if request.method == 'DELETE':
        ack = portfolioData.removeTransaction(client, portfolioId, int(transactionId))
        return webio.json(ack)

@portfolio_api.route('/<portfolioId>/holdings')
def portfolioHoldings(portfolioId):
    return webio.json(webio.df2dict(Portfolio(portfolioId, client).holdings()))

@portfolio_api.route('/<portfolioId>/nav')
def portfolioNav(portfolioId):
    return webio.json(webio.ts2dict(Portfolio(portfolioId, client).nav()))

@portfolio_api.route('/<portfolioId>/return/<window>')
def portfolioReturn(portfolioId, window):
    return webio.json(webio.ts2dict(Portfolio(portfolioId, client).rollingReturn(window)))

@portfolio_api.route('/<portfolioId>/return-stats')
def portfolioReturnStats(portfolioId):
    return webio.json(Portfolio(portfolioId, client).returnStats())
