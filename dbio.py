import constants
import hashlib
import datetime
from utils import ist

def dictFilter( d, keys ):
    return( {k: v for k, v in d.items() if k in keys } )

# example schemeCode = "101671"
def fundNav( client, schemeCode ):
    data = client.fundData( { constants.SCHEMECODE_KEY : schemeCode } )
    if( data.count() == 1 ):
        dates = data[0][ constants.NAV_DATES_KEY ];
        values = [ float( i ) for i in data[0][ constants.NAV_VALUES_KEY ] ];
        nav = { constants.DATES_KEY : [ d for d in dates ], constants.VALUES_KEY : values };
    else:
        nav = { constants.DATES_KEY : [], constants.VALUES_KEY : [] };
    return( nav );

# pass in navDate to get schemes with NAV on that date
def fundSchemes( client, navDate=None ):
    schemeCols = dict( [ (key,1) for key in constants.SCHEME_ATTRIBUTES ] );
    schemeCols[ constants.MONGO_ID ] = 0;
    filterCols = {}
    if navDate is not None:
        filterCols[ constants.NAV_DATES_KEY ] = navDate
    # some day we should also be able to return nav for given navDate
    data = client.fundData( filterCols, schemeCols );
    return( [ scheme for scheme in data ] );

def fundScheme( client, schemeCode ):
    schemeCols = dict( [ (key,1) for key in constants.SCHEME_ATTRIBUTES ] );
    schemeCols[ constants.MONGO_ID ] = 0;
    data = client.fundData( { constants.SCHEMECODE_KEY : schemeCode }, schemeCols );
    if( data.count() == 1 ):
        data = data[0]
    else:
        data = {};
    return( data );

def portfolioId( clientName, portfolioName ):
    s = clientName + portfolioName;
    Id = hashlib.md5( s.encode( 'utf-8' ) );
    return( Id.hexdigest() );

def newTransactionId( transactions ):
    if len( transactions ) > 0:
        return max( [ T[ constants.TRANSACTION_ID ] for T in transactions ] ) + 1;
    else:
        return 0;

def newPortfolio( Id, clientName, portfolioName ):
    now = ist.localize(datetime.datetime.today())
    return( {
        constants.PORTFOLIO_ID : Id,
        constants.CLIENT_NAME : clientName,
        constants.PORTFOLIO_NAME : portfolioName,
        constants.TRANSACTIONS : [],
        constants.DATE_CREATED : now
    } );

def newTransaction( Id, schemeCode, schemeName, cashflow, quantity, date ):
    return( {
        constants.TRANSACTION_ID : Id,
        constants.ASSET_CODE : schemeCode,
        constants.ASSET_NAME : schemeName,
        constants.TXN_CASHFLOW : cashflow,
        constants.TXN_QUANTITY : quantity,
        constants.TXN_DATE : date
    } )

def addPortfolio( client, clientName, portfolioName ):
    Id = portfolioId( clientName, portfolioName );
    data = client.portfolioData( { constants.PORTFOLIO_ID : Id } );
    if( data.count() > 0 ):
        return False;
    return( client.addPortfolio( newPortfolio( Id, clientName, portfolioName ) ) );

def transactions( client, portfolioId ):
    data = client.portfolioData( { constants.PORTFOLIO_ID : portfolioId } );
    if( data.count() == 1 ):
        Ts = data[0][ constants.TRANSACTIONS ]
    else:
        Ts = [];
    return( Ts );

def portfolioData( client, portfolioId ):
    data = client.portfolioData( { constants.PORTFOLIO_ID : portfolioId }, { constants.MONGO_ID : 0 } );
    if( data.count() == 1 ):
        P = data[0]
    else:
        P = {};
    return( P );

def clientPortfolios( client, clientName ):
    schemeCols = dict( [ (key,1) for key in [ constants.PORTFOLIO_ID, constants.PORTFOLIO_NAME, constants.DATE_CREATED ] ] );
    schemeCols[ constants.MONGO_ID ] = 0;   # repeated Code
    data = client.portfolioData( { constants.CLIENT_NAME : clientName }, schemeCols );
    return( [ scheme for scheme in data ] );
    
def addTransaction( client, portfolioId, schemeCode, schemeName, cashflow, quantity, date ):
    Ts = transactions( client, portfolioId );
    transactionId = newTransactionId( Ts );
    Ts.append( newTransaction( transactionId, schemeCode, schemeName, cashflow, quantity, date ) );
    return( client.updatePortfolio( { constants.PORTFOLIO_ID : portfolioId }, { constants.TRANSACTIONS : Ts } ) );

def removeTransaction( client, portfolioId, transactionId ):
    Ts = [ txn for txn in transactions( client, portfolioId ) if txn.get(constants.TRANSACTION_ID) != transactionId ]
    return( client.updatePortfolio( { constants.PORTFOLIO_ID : portfolioId }, { constants.TRANSACTIONS: Ts } ) )