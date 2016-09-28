from flask import jsonify
from flask.json import JSONEncoder
import calendar
from datetime import datetime
from dateutil.parser import parse
import constants

# parse ISO date string to datetime
def dateParser(dateStr):
    return parse(dateStr);

def json( data ):
    return( jsonify( { constants.JSON_KEY : data } ) );

# set this on the flask.json_encoder to encode dates in isoformat
class customJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                serial = obj.isoformat()
                return serial
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
