from datetime import datetime
import io
import zipfile
import requests
from flask import jsonify
from flask import request
from flask.json import JSONEncoder
from bson.objectid import ObjectId
import pandas as pd
import entropy.utils.dateandtime as dtu

# ts2dict and dict2t
VALUES_KEY = "values"
DATES_KEY = "dates"

# all http responses will be of the form {data : <>}
JSON_KEY = "data"
JSON_ERROR_KEY = "error"

ALLOWED_EXTENSIONS = set(['csv', 'xls'])

def json(data):
    return jsonify({JSON_KEY : data})

def err(e):
    return jsonify({JSON_ERROR_KEY: str(e)})

# we have 2 different ways of converting to list of dicts
# based on convenience of manipulating timeseries dataframes vs general dataframes

def ts2dict(df):
    '''convert dataframe whose index is datetime series
    to {dates: df.index, col1: [...], col2: [...], etc}
    '''
    # Alternative:
    # return {DATES_KEY: list(df.index), VALUES_KEY: df.to_dict('list')}
    dct = df.to_dict('list')
    dct[DATES_KEY] = list(df.index)
    return dct

def df2dict(df):
    '''convert dataframe whose index is an object other than date
    to [{col1: [...], col2: [...]}]
    '''
    df = df.reset_index()
    return df.to_dict('records')

# use this for _nav? Or just get rid of it.
def dict2ts(dct):
    df = pd.DataFrame(dct).set_index(DATES_KEY)
    df.index.rename(None, inplace=True)
    return df

def requestWithTries(url, params={}):
    counter = 3
    # retry 3 times to handle internet timeouts or network issues
    while counter > 0:
        try:
            resp = requests.get(url, params)
            counter = 0
        except Exception:
            counter = counter - 1
    return resp

def fileContentFromUrl(url, params={}):
    res = requestWithTries(url, params)
    return io.BytesIO(res.content)

def unzippedFileFromUrl(url, params={}):
    filename = fileContentFromUrl(url, params)
    return zipfile.ZipFile(filename)

def allowedFile(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getUploadedFile():
    if 'file' not in request.files:
        raise RuntimeError('No file part')
    file = request.files['file']
    if file.filename == '':
        raise RuntimeError('No selected file')
    if file and allowedFile(file.filename):
        return file
    raise RuntimeError('Selected file is invalid')

# set this on the flask.json_encoder to encode dates in isoformat
class customJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                # python does not really conform to ISO 8601
                # it is not tz aware unless the TZ is explicitly set
                serial = dtu.localizeToTz(obj).isoformat()
                return serial
            elif isinstance(obj, ObjectId):
                serial = str(obj)
                return serial
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
