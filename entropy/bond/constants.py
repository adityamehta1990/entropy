import entropy.asset.constants as ac

ASSET_TYPE_KEY = ac.ASSET_TYPE_KEY
ASSET_TYPE_BOND = "bond"
ASSET_TYPE_DEBENTURE = "debenture"

TICKER = 'ticker'
BOND_NAME = 'bondName'
BOND_STATUS = 'status'
BOND_GROUP = 'group'
FACE_VALUE = 'faceValue'
ISIN = 'ISIN'
INDUSTRY = 'industry'
BOND_CODE_BSE = "bseCode" # dont project in fund attributes, this is required only internally
ASSET_CLASS = 'assetClass'

BOND_ATTRIBUTES = [TICKER, BOND_NAME, BOND_STATUS, BOND_GROUP, FACE_VALUE, ISIN, INDUSTRY, \
                ASSET_TYPE_KEY, ASSET_CLASS]
