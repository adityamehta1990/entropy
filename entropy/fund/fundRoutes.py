from flask import Blueprint
from flask import request
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

@fund_api.route('/fund/<_id>', methods=['GET'])
def getFundInfo(_id):
    return utils.json(Fund(_id,client).fundInfo())

@fund_api.route('/enriched/<_id>')
def enrichedFundInfo(_id):
    return utils.json(fundData.enrichedFundInfo(client, _id))

@fund_api.route('/fund/<_id>', methods=['POST'])
def updateFundInfo(_id):
    fundInfo = request.get_json()
    return utils.json(fundData.updateFundInfo(client, _id, fundInfo))

@fund_api.route('/nav/<_id>')
def getFundNav(_id):
    return utils.json(utils.ts2dict(Fund(_id, client).nav()))

@fund_api.route('/return/<_id>/<window>')
def getFundReturn(_id, window):
    return utils.json(utils.ts2dict(Fund(_id, client).rollingReturn(window)))
