from flask import Blueprint
from entropy.db import dbclient
from entropy.utils import utils
from entropy.fund.fund import Fund
from entropy.fund import fundData

fund_api = Blueprint('fund_api',__name__)
client = dbclient.MClient()

# fund Page
@fund_api.route('/funds')
def getFundList():
    return utils.json(fundData.fundList(client))

@fund_api.route('/funds/<navDate>')
def getFundListOnDate(navDate):
    return utils.json(fundData.fundList(client, utils.dateParser(navDate)))

@fund_api.route('/fund/<_id>')
def getFundScheme(_id):
    return utils.json(Fund(_id,client).fundInfo())

@fund_api.route('/nav/<_id>')
def getFundNav(_id):
    return utils.json(utils.ts2dict(Fund(_id, client).nav()))

@fund_api.route('/return/<_id>/<window>')
def getFundReturn(_id, window):
    return utils.json(utils.ts2dict(Fund(_id, client).rollingReturn(window)))
