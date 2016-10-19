from pymongo import MongoClient

class MClient():
    def __init__( self ):
        client = MongoClient();
        fundDb = client.fund_db;
        self.fundDataColl = fundDb.fund_data;
        self.portfolioDataColl = fundDb.portfolio_data;
    
    def fundData( self, filterCondition, keys={} ):
        if( len( keys ) == 0 ):
            return self.fundDataColl.find( filterCondition );
        else:
            return self.fundDataColl.find( filterCondition, keys );
    
    def updateFundData( self, filterCondition, item ):
        result = self.fundDataColl.update_one( filterCondition, { "$set" : item } )
        return result.acknowledged

    def portfolioData( self, filterCondition, keys={} ):
        if( len( keys ) == 0 ):
            return self.portfolioDataColl.find( filterCondition );
        else:
            return self.portfolioDataColl.find( filterCondition, keys );
    
    def addPortfolio( self, item ):
        result = self.portfolioDataColl.insert_one( item );     # todo: dateCreated
        return result.acknowledged;
        
    def updatePortfolio( self, filterCondition, item ):
        result = self.portfolioDataColl.update_one( filterCondition, { "$set" : item } );   # todo: lastUpdated
        return result.acknowledged;
