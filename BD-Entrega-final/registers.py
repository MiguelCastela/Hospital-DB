import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager
import funções_globais as glb






def add_patient():
    glb.logger.info('POST /patient')
    data = flask.request.json
    conn = glb.db_connection()
    cur = conn.cursor()


    # verify that data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['birthday', 'id_user_cc', 'username', 'nationality', 'password', 'email'])
    if len(missing) > 0:
        response = {
            'status': glb.StatusCodes['api_error'],
            'errors': f'Missing fields: {missing}'
        }
        return flask.jsonify(response)


    try:
        # begin the transaction
        cur.execute("BEGIN;")

        cur.execute("LOCK TABLE patient IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE utilizador IN ACCESS EXCLUSIVE MODE;")

        # get the data from the request and return id
        valores = (data['birthday'], data['id_user_cc'], data['username'], data['nationality'], data['password'], data['email'])

        # try to create the user
        query = """
        INSERT INTO utilizador (birthday, id_user_cc, name_, nationality, password_, mail) 
        VALUES(%s,%s,%s,%s,%s,%s) 
        RETURNING id;
        """
        cur.execute(query, valores)
        user_id = cur.fetchone()[0]

        # try to create the patient, with user_id as foreign key
        query_2 = """INSERT INTO patient (utilizador_id) VALUES(%s);"""
        cur.execute(query_2, str(user_id))

        # commit the transaction
        cur.execute("COMMIT;")


    # rollback transaction and inform frontend
    except(Exception, psycopg2.Error) as error:
        if(conn):
            glb.logger.error("Failed to register patient: ", error)
            print("Failed to insert record into mobile table: ", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }

        # rollback the transaction
        cur.execute("ROLLBACK;")
        return flask.jsonify(response)
    

    else:
        glb.logger.info("Patient registered successfully")
        response = {
            'status': glb.StatusCodes['success'],
            'message': 'Patient registered successfully',
            'id': user_id
        }
        return flask.jsonify(response)


    finally:
        if(conn):
            cur.close()
            conn.close()



def add_assistant():
    glb.logger.info('POST /assistant')
    data = flask.request.json
    conn = glb.db_connection()
    cur = conn.cursor()

    # verify that data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['birthday', 'id_user_cc', 'username', 'nationality', 'password', 'email'])
    if len(missing) > 0:
        response = {
            'status': glb.StatusCodes['api_error'],
            'errors': f'Missing fields: {missing}'
        }
        return flask.jsonify(response)


    try:
        # begin the transaction
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE employee IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE assistant IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE utilizador IN ACCESS EXCLUSIVE MODE;")


        # get the data from the request and return id
        valores = (data['birthday'], data['id_user_cc'], data['username'], data['nationality'], data['password'], data['email'])

        # try to create the user
        query = """
        INSERT INTO utilizador (birthday, id_user_cc, name_, nationality, password_, mail) 
        VALUES(%s,%s,%s,%s,%s,%s) 
        RETURNING id;
        """
        cur.execute(query, valores)
        user_id = cur.fetchone()[0]

        # try to create employee with user_id as foreign key
        query = """
        INSERT INTO employee (utilizador_id)
        VALUES(%s);
        """
        cur.execute(query, str(user_id))

        query = """
        INSERT INTO assistant (employee_utilizador_id)
        VALUES(%s);
        """
        cur.execute(query, str(user_id))


        # commit the transaction
        cur.execute("COMMIT;")
    

    # rollback transaction and inform frontend
    except(Exception, psycopg2.Error) as error:
        if(conn):
            glb.logger.error("Failed to register assistant: ", error)
            print("Failed to insert record into mobile table", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }

        # rollback the transaction
        cur.execute("ROLLBACK;")
        return flask.jsonify(response)
    

    else:
        glb.logger.info("Assistant registered successfully")
        response = {
            'status': glb.StatusCodes['success'],
            'message': 'Assistant registered successfully',
            'id': user_id
        }
        return flask.jsonify(response)
    

    finally:
        if(conn):
            cur.close()
            conn.close()



def add_nurse():
    glb.logger.info('POST /nurse')
    data = flask.request.json
    conn = glb.db_connection()
    cur = conn.cursor()

    # verify that data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['birthday', 'id_user_cc', 'username', 'nationality', 'password', 'email', 'category_category_name'])
    if len(missing) > 0:
        response = {
            'status': glb.StatusCodes['api_error'],
            'errors': f'Missing fields: {missing}'
        }
        return flask.jsonify(response)


    try:
        # begin the transaction
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE employee IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE nurse IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE category IN ACCESS EXCLUSIVE MODE;")


        # check if the category exists in the table "category"
        query = """
        SELECT * FROM category WHERE category_name = %s;
        """
        cur.execute(query, (data['category_category_name'],))
        if cur.rowcount == 0:
            glb.logger.error("Category does not exist")
            response = {
                'status': glb.StatusCodes['invalid category'],
                'errors': f'Category does not exist'
            }
            return flask.jsonify(response)
        


        # get the data from the request
        valores = (data['birthday'], data['id_user_cc'], data['username'], data['nationality'], data['password'], data['email'])

        # try to create the user
        query = """
        INSERT INTO utilizador (birthday, id_user_cc, name_, nationality, password_, mail) 
        VALUES(%s,%s,%s,%s,%s,%s) 
        RETURNING id;
        """
        cur.execute(query, valores)
        user_id = cur.fetchone()[0]

        # try to create employee with user_id as foreign key
        query = """
        INSERT INTO employee (utilizador_id)
        VALUES(%s);
        """
        cur.execute(query, str(user_id))

        # get the data from the request
        valores = (data['category_category_name'], str(user_id))

        # try to create nurse with attribute category and user_id as foreign key
        query = """
        INSERT INTO nurse (category_category_name, employee_utilizador_id)
        VALUES(%s, %s);
        """
        cur.execute(query, valores)


        # commit the transaction
        cur.execute("COMMIT;")
    

    # rollback transaction and inform frontend
    except(Exception, psycopg2.Error) as error:
        if(conn):
            glb.logger.error("Failed to register nurse: ", error)
            print("Failed to insert record into mobile table", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }

        # rollback the transaction
        cur.execute("ROLLBACK;")
        return flask.jsonify(response)
    

    else:
        glb.logger.info("Nurse registered successfully")
        response = {
            'status': glb.StatusCodes['success'],
            'message': 'Nurse registered successfully',
            'id': user_id
        }
        return flask.jsonify(response)
    

    finally:
        if(conn):
            cur.close()
            conn.close()



def add_doctor():
    glb.logger.info('POST /doctor')
    data = flask.request.json
    conn = glb.db_connection()
    cur = conn.cursor()

    # verify that data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['birthday', 'id_user_cc', 'username', 'nationality', 'password', 'email', 'medical_license_id', 'university', 'specialization_expertise'])
    if len(missing) > 0:
        response = {
            'status': glb.StatusCodes['api_error'],
            'errors': f'Missing fields: {missing}'
        }
        return flask.jsonify(response)


    try:
        # begin the transaction
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE employee IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE doctor IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE specialization IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE utilizador IN ACCESS EXCLUSIVE MODE;")


        # check if the specialization_expertise exists in the table "specialization"
        query = """
        SELECT * FROM specialization WHERE expertise = %s;
        """
        cur.execute(query, (data['specialization_expertise'],))
        if cur.rowcount == 0:
            glb.logger.error("Specialization does not exist")
            response = {
                'status': glb.StatusCodes['invalid specialization'],
                'errors': f'Specialization does not exist'
            }
            return flask.jsonify(response)


        # get the data from the request
        valores = (data['birthday'], data['id_user_cc'], data['username'], data['nationality'], data['password'], data['email'])

        # try to create the user
        query = """
        INSERT INTO utilizador (birthday, id_user_cc, name_, nationality, password_ , mail) 
        VALUES(%s,%s,%s,%s,%s,%s) 
        RETURNING id;
        """
        cur.execute(query, valores)
        user_id = cur.fetchone()[0]

        # try to create employee with user_id as foreign key
        query = """
        INSERT INTO employee (utilizador_id)
        VALUES(%s);
        """
        cur.execute(query, str(user_id))

        # get the data from the request
        valores = (data['medical_license_id'], data['university'], data['specialization_expertise'] , str(user_id))

        # try to create doctor with attributes in 'valores' and user_id as foreign key
        query = """
        INSERT INTO doctor (medical_license_id, university, specialization_expertise, employee_utilizador_id)
        VALUES(%s, %s, %s, %s);
        """
        cur.execute(query, valores)


        # commit the transaction
        cur.execute("COMMIT;")
    

    # rollback transaction and inform frontend
    except(Exception, psycopg2.Error) as error:
        if(conn):
            glb.logger.error("Failed to register doctor: ", error)
            print("Failed to insert record into mobile table", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }

        # rollback the transaction
        cur.execute("ROLLBACK;")
        return flask.jsonify(response)
    

    else:
        glb.logger.info("Doctor registered successfully")
        response = {
            'status': glb.StatusCodes['success'],
            'message': 'Doctor registered successfully',
            'id': user_id
        }
        return flask.jsonify(response)


    finally:
        if(conn):
            cur.close()
            conn.close()
