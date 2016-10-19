import dbclient
import constants
import pandas as pd
from fund import Fund
from investment import Investment

class Portfolio(Investment):
    portfolioId=None
    client=None
    
    # we can store portfolio data here and use it directly
    # if someone passes an invalid portfolioId, that can be caught in __init__

    def __init__(self,portfolioId,client):
        self.portfolioId=portfolioId
        self.client=client

    def portfolioData(self):
        data = self.client.portfolioData( { constants.PORTFOLIO_ID : self.portfolioId }, { constants.MONGO_ID : 0, constants.TRANSACTIONS : 0 } );
        if( data.count() == 1 ):
            P = data[0]
        else:
            P = {}
        return( P )

    def transactions(self):
        data = self.client.portfolioData( { constants.PORTFOLIO_ID : self.portfolioId } );
        if( data.count() == 1 ):
            Ts = data[0][ constants.TRANSACTIONS ]
        else:
            Ts = []
        return( Ts )
    
    def nav(self):
        txns = pd.DataFrame( self.transactions() )
        aggregateTxns = txns.groupby(by=['date','schemeCode']).agg({'cashflow':sum,'quantity':sum})
        aggregateTxns = aggregateTxns.reset_index().set_index('date')
        aggregateTxns['cum_quantity'] = aggregateTxns.quantity.cumsum()
        qty = aggregateTxns.pivot(columns='schemeCode',values='cum_quantity')

        # get all fund navs to avoid dup calls to db
        schemeCodes = aggregateTxns.schemeCode.unique()
        nav = pd.Series([],[])
        for schemeCode in schemeCodes:
            schemeNav = Fund(schemeCode,self.client).nav()
            nav = nav.add(qty.get(schemeCode).reindex(schemeNav.index,method='pad') * schemeNav,fill_value=0)
        
        return(nav.dropna())