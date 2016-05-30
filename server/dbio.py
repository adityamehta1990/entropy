from pymongo import MongoClient

schemeCodeKey = "schemeCode";
navDatesKey = "navDates";
navValuesKey = "nav";
datesKey = "dates";
valuesKey = "values";

def dictFilter( d, keys ):
    return( {k: v for k, v in d.items() if k in keys } )

def getDb( client ):
    return client.fund_db;

def fundData( db ):
    return db.fund_data;

# example schemeCode = "101671"
def fundNav( schemeCode ):
    client = MongoClient();
    db = getDb(client);
    coll = fundData( db );
    client.close();
    data = coll.find( { schemeCodeKey : schemeCode } );
    if( data.count() == 1 ):
        nav = { datesKey : data[0][ navDatesKey ], valuesKey : data[0][ navValuesKey ] };
    else:
        nav = { datesKey : [], valuesKey : [] };
    return( nav );