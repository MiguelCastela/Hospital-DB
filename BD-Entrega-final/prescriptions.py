import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager, get_jwt_identity, get_jwt
import funções_globais as glb

def get_prescriptions(patient_id):
    glb.logger.info('GET /dbproj/prescriptions')
    token = get_jwt_identity()
    claims = get_jwt()

    #apenas funcionários podem aceder a esta informação ou o próprio paciente
    # (pacientes que não sejam o próprio paciente não podem aceder a esta informação)
    if (claims=='patient' and token!=patient_id):
        return flask.jsonify({'error': 'Unauthorized'}), 401
    
    conn = glb.db_connection()
    cur = conn.cursor()

    try:

        cur.execute('BEGIN;')
        cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")

        '''
        cur.execute("""
            SELECT prescription.* FROM prescription
            JOIN hospitalization ON prescription.hospitalization_hospitalization_id = hospitalization.hospitalization_id
            JOIN appointment ON prescription.appointment_appointment_id = appointment.appointment_id
            WHERE appointment.patient_utilizador_id = %s OR hospitalization.patient_utilizador_id = %s;
            """, (patient_id))
        prescriptions_hosp = cur.fetchall()
        '''
                
        #obter as prescrições de um paciente
        cur.execute(""" 
            SELECT prescription.* FROM prescription
            JOIN appointment ON prescription.appointment_appointment_id = appointment.appointment_id
            WHERE appointment.patient_utilizador_id = %s;
            """, (patient_id,))
        prescriptions_apt = cur.fetchall()

        
        cur.execute("""
            SELECT prescription.* FROM prescription
            JOIN hospitalization ON prescription.hospitalization_hospitalization_id = hospitalization.hospitalization_id
            WHERE hospitalization.patient_utilizador_id = %s;
            """, (patient_id,))
        prescriptions_hosp = cur.fetchall()

        prescriptions = prescriptions_apt + prescriptions_hosp
        print("prescriptions: ")
        #ir buscar os detalhes da prescrição
        medication_details = []
        for prescription in prescriptions:
            print(prescription)
            cur.execute("""
                SELECT medication_medication_id, medication_ammount, frequency FROM quantity
                JOIN medication ON quantity.medication_medication_id = medication_id
                WHERE quantity.prescription_id_prescription = %s;
                """, (prescription[2], ))
        medication_details.append(cur.fetchall())

        cur.execute("COMMIT;")


    except(Exception, psycopg2.DatabaseError) as error:
        cur.execute("ROLLBACK;")
        glb.logger.error(f'GET /dbproj/prescriptions - error: {error}')
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': str(error)
        }
        return flask.jsonify(response)


    else:
        print(prescriptions)
        lista = []
        for prescription in prescriptions:
            if prescription[1] is not None:
                presc = {
                'prescription_id' : prescription[0],
                'hospitalization_id' : prescription[1],
                }
            else:
                presc = {
                'prescription_id' : prescription[0],
                'appointment_id' : prescription[2],
                
                }
            lista.append(presc)
            print(lista)
        response = {
            'status': glb.StatusCodes['success'],
            'results': lista
        }
        return flask.jsonify(response)


    finally:
        if cur is not None:
            cur.close()



def add_prescription():
    #hospitalization_id, appointment_id, medication_id, medication_amount
    token = get_jwt_identity()
    claims = get_jwt()
    print("claims: ", claims)

    if claims['role'] != 'doctor':
        return flask.jsonify({'error': 'Unauthorized'}), 401

    data = flask.request.get_json()
    print("data: ", data)

    conn = glb.db_connection()
    cur = conn.cursor()


    # verify if data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['type', 'event_id', 'validity', 'medicines'])
    if len(missing) > 0:
        response = {
            'status': glb.StatusCodes['api_error'],
            'errors': f'Missing fields: {", ".join(missing)}'
        }
        return flask.jsonify(response), 400
    for medication in data['medicines']:
        missing = glb.check_missingfirelds(medication, ['medicine', 'posology_dose', 'posology_frequency'])
        if len(missing) > 0:
            response = {
                'status': glb.StatusCodes['api_error'],
                'errors': f'Missing fields: {", ".join(missing)}'
            }
            return flask.jsonify(response), 400


    try:
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE prescription IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE medication IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE quantity IN ACCESS EXCLUSIVE MODE;")
        #caso não tenha hospitalização nem consulta associada
        hospitalization_id = None
        appointment_id = None

        if data['type'] == 'hospitalization':
            hospitalization_id = data['event_id']
        elif data['type'] == 'appointment':
            appointment_id = data['event_id']
        else:
            return flask.jsonify({'error': 'Invalid type'}), 400


        validity = data['validity']
        #caso tenha hospitalização ou consulta associada
        cur.execute("""
            INSERT INTO prescription (hospitalization_hospitalization_id, appointment_appointment_id, validity)
            VALUES (%s, %s, %s)
            RETURNING id_prescription;
            """, (hospitalization_id, appointment_id, validity))
    
        # Obter o ID da nova prescrição
        prescription_id = cur.fetchone()[0]

        for medication in data['medicines']:
            #procurar o id da medicação
            cur.execute("""
                SELECT medication_id FROM medication WHERE medication_name = %s;
                """, (medication["medicine"],))
            medication_id = cur.fetchone()[0]
            if medication_id is None:
                return flask.jsonify({'error': 'Medication not found'}), 400
            cur.execute(""" INSERT INTO quantity (medication_ammount, frequency, medication_medication_id, prescription_id_prescription) 
                            VALUES (%s, %s, %s, %s)""",
                            (medication["posology_dose"], medication["posology_frequency"], medication_id, prescription_id))
    
        # commit the transaction
        cur.execute("COMMIT;")

    except(Exception, psycopg2.DatabaseError) as error:
        glb.logger.error(f'POST /dbproj/surgery - error: {error}')
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': str(error)
        }
        cur.execute("ROLLBACK;")
        return flask.jsonify(response)
    
    else:
        response = {
            'status': glb.StatusCodes['success'],
            'results': { 'prescription_id': prescription_id }
        }
        return flask.jsonify(response)
    
    finally:
        cur.execute("COMMIT;")

        if cur is not None:
            cur.close()
        
