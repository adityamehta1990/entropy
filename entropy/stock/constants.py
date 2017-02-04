import entropy.asset.constants as ac

ASSET_TYPE_KEY = ac.ASSET_TYPE_KEY
ASSET_TYPE_STOCK = "stock"

TICKER = 'ticker'
STOCK_NAME = 'stockName'
STOCK_STATUS = 'status'
STOCK_GROUP = 'group'
FACE_VALUE = 'faceValue'
ISIN = 'ISIN'
INDUSTRY = 'industry'
STOCK_CODE_BSE = "bseCode" # dont project in fund attributes, this is required only internally
ASSET_CLASS = 'assetClass'

STOCK_ATTRIBUTES = [TICKER, STOCK_NAME, STOCK_STATUS, STOCK_GROUP, FACE_VALUE, ISIN, INDUSTRY, \
                ASSET_TYPE_KEY, ASSET_CLASS]
