import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager, get_jwt_identity
import funções_globais as glb






def execute_payment(billing_bill_id):
    glb.logger.info('POST /patient')

    data = flask.request.json
    conn = glb.db_connection()
    cur = conn.cursor()


    # verify if the request has all the necessary fields
    missing = glb.check_missingfirelds(data, ['amount', 'method'])
    if missing:
        response = {
            'status': glb.StatusCodes['api_error'],
            'errors': f'Missing fields: {", ".join(missing)}'
        }
        return flask.jsonify(response)
    
    
    try:
        # begin the transaction
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE billing IN SHARE ROW EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE payment IN SHARE ROW EXCLUSIVE MODE;")

        # get the data from the request and return id
        valores = (data['amount'], data['method'], billing_bill_id)

        # look for the bill
        query = """
        SELECT patient_utilizador_id
        FROM appointment
        WHERE billing_bill_id = %s

        UNION
        
        SELECT patient_utilizador_id
        FROM hospitalization
        WHERE billing_bill_id = %s;
        """
        cur.execute(query, (billing_bill_id, billing_bill_id,))

        # if the bill does not exist, return an error
        if cur.rowcount == 0:
            response = {
                'status': glb.StatusCodes['api_error'],
                'errors': 'Bill does not exist'
            }
            return flask.jsonify(response)
        
    
        # if the bill exists, get the patient id
        patient_id = cur.fetchone()[0]

        # verify if the patient is the one who is trying to pay
        if patient_id != get_jwt_identity():
            response = {
                'status': glb.StatusCodes['api_error'],
                'errors': 'You are not allowed to pay this bill'
            }
            return flask.jsonify(response)

        # verify if the sum of the payments is equal to the bill
        query = """
        SELECT COALESCE(SUM(amount), 0)
        FROM payment
        WHERE billing_bill_id = %s;
        """
        cur.execute(query, (billing_bill_id,))
        payment_sum = cur.fetchone()[0]
    
        # get bill cost
        query = """
        SELECT cost
        FROM billing
        WHERE bill_id = %s;
        """
        cur.execute(query, (billing_bill_id,))
        bill_cost = cur.fetchone()[0]

        if int(payment_sum) +int(data['amount']) > int(bill_cost):
            response = {
                'status': glb.StatusCodes['api_error'],
                'errors': 'You are trying to pay more than the bill or a bill already paid'
            }
            return flask.jsonify(response)
    
        # try to create the payment
        query = """
        INSERT INTO payment (date_payment, amount, method, billing_bill_id)
        VALUES( CURRENT_DATE, %s, %s, %s )
        RETURNING payment_id;
        """
        cur.execute(query, valores)
        rows = cur.fetchall()
        cur.execute("COMMIT;")


    except(Exception, psycopg2.Error) as error:
        cur.execute("ROLLBACK;")
        if(conn):
            glb.logger.error("Failed to pay bill: ", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }

        # rollback the transaction
        cur.execute("ROLLBACK;")
        return flask.jsonify(response)
    

    else:
        glb.logger.info("bill paid successfull")
        response = {
            'status': glb.StatusCodes['success'],
            'results': bill_cost - payment_sum - data['amount']
        }
        return flask.jsonify(response)


    finally:
        if(conn):
            cur.close()
            conn.close()