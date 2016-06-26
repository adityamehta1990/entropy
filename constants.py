# get requests
JSON_KEY = "data";

# db constants
SCHEMECODE_KEY = "schemeCode";
NAV_DATES_KEY = "navDates";
NAV_VALUES_KEY = "nav";
MONGO_ID = "_id";

# db <-> pandas
DATES_KEY = "dates";
VALUES_KEY = "values";

# fund-data
SCHEME_ATTRIBUTES = [ "schemeName", "schemeCode", "schemeType", "fundName" ];

# portfolio
CLIENT_NAME = "clientName";
PORTFOLIO_ID = "portfolioId";
PORTFOLIO_NAME = "portfolioName";
TRANSACTIONS = "transactions";
DATE_CREATED = "dateCreated";

# transactions
TRANSACTION_ID = "transactionId";
ASSET_CODE = SCHEMECODE_KEY;
QUANTITY = "quantity";
PRICE = "price";
DATE = "date";

# analytics constants
NUMDAYS = { "1d" : 1, "1w" : 5, "1m" : 21, "3m" : 63, "6m" : 126, "1y" : 252, "2y" : 504, "5y" : 1260 };
