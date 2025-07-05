import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager


db_connection = None
logger = logging.getLogger('logger')

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

#DATABASE ACCESS

def db_connection():
    db = psycopg2.connect(
        user='aulaspl',
        password='aulaspl',
        host='127.0.0.1',
        port='5432',
        database='projeto'
    )

    return db
#ENDPOINTS



def check_missingfirelds(data, fields):
    # verify if data contains all the necessary fields
    missing = [field for field in fields if field not in data]
    if len(missing) > 0:
        print("missing fields")
        logger.error(f"Missing fields: {', '.join(missing)}")
    return missing