import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager, get_jwt_identity
import funções_globais as glb


def print_jwt_info():
    identity = get_jwt_identity()
    jwt_claims = get_jwt()

    print(f"Identity: {identity}")
    print(f"Role: {jwt_claims['role']}")


def authenticate_user():
    glb.logger.info('POST /login')
    data = flask.request.json

    conn = glb.db_connection()
    cur = conn.cursor()

    valores = (data['mail'], data['password_'])
    try:
        cur.execute('BEGIN')

        query = """SELECT id FROM utilizador WHERE mail = %s AND password_ = %s"""
        cur.execute(query, valores)
        id = cur.fetchone()[0]


        if id is None:
            print("User not found or password incorrect")
            response = {
                'status': glb.StatusCodes['bad_request'],
                'errors': 'User not found or password incorrect'
            }
            return flask.jsonify(response)
        
        role = None 
        tables = {
            'patient': 'utilizador_id',
            'assistant': 'employee_utilizador_id',
            'nurse': 'employee_utilizador_id',
            'doctor': 'employee_utilizador_id',
        }

        for table, id_column in tables.items():
            query = f"""
                    SELECT 1 FROM {table}
                    WHERE {id_column} = %s 
                    """
            cur.execute(query, (id,))
            if cur.fetchone() is not None:
                role = table
                break

        if role is None:
            response = {
                'status': glb.StatusCodes['bad_request'],
                'errors': 'User has no role'
            }
            return flask.jsonify(response)

        additional_claims = {'role': role}
        access_token = create_access_token(identity=id, additional_claims=additional_claims)
        #access_token = create_access_token(identity=id)

        cur.execute('COMMIT')

        response = flask.jsonify({
            'status': glb.StatusCodes['success'],
            'results': {
                'id': id,
                'role': role,
                'access_token': access_token
            }
        })

    except(Exception, psycopg2.Error) as error:
        cur.execute('ROLLBACK')
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }
        return flask.jsonify(response)

    finally:
        if(conn):
            cur.close()
            conn.close()

        return response