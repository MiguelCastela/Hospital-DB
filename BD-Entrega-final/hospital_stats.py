import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager
import funções_globais as glb


def list_top3():
    glb.logger.info('GET /top3')
    glb.logger.info('top3 DOES NOT WORK YET')
    conn = glb.db_connection()
    cur = conn.cursor()
    claims = get_jwt()
    if claims['role'] != 'assistant':
        return flask.jsonify({'error': 'Unauthorized'}), 401

    try:
        cur.execute("BEGIN;")  
        cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
        cur.execute("LOCK TABLE appointment IN SHARE MODE;")
        cur.execute("LOCK TABLE hospitalization IN SHARE MODE;")
        cur.execute("LOCK TABLE billing IN SHARE MODE;")
        cur.execute("LOCK TABLE payment IN SHARE MODE;")

        # Get the top 3 patients considering the money spent in the Hospital for the current month. The result should discriminate the respective procedures’ details. Just one SQL query should be used to obtain the information. Only assistants can use this endpoint.
        query = """
                WITH top_patients AS (
                    SELECT patient_utilizador_id AS patient_id, SUM(amount) AS total_paid
                    FROM payment 
                    JOIN billing ON payment.billing_bill_id = billing.bill_id 
                    JOIN (
                        SELECT billing_bill_id, patient_utilizador_id FROM appointment 
                        UNION ALL
                        SELECT billing_bill_id, patient_utilizador_id FROM hospitalization 
                    ) AS bill_user ON billing.bill_id = bill_user.billing_bill_id
                    WHERE date_payment >= NOW() - INTERVAL '30 days' 
                    GROUP BY patient_utilizador_id 
                    ORDER BY total_paid DESC 
                    LIMIT 3) 

                SELECT util.name_, topp.total_paid, 
                    array_agg(json_build_object('procedure_id', COALESCE(appt.appointment_id, hosp.hospitalization_id), 
                                                'doctor_id', COALESCE(appt.doctor_employee_utilizador_id, hosp.nurse_employee_utilizador_id), 
                                                'date', COALESCE(appt.appointment_date, hosp.start_date))) AS procedures

                FROM top_patients topp
                JOIN patient pat ON topp.patient_id = pat.utilizador_id 
                JOIN utilizador util ON pat.utilizador_id = util.id 
                LEFT JOIN appointment appt ON topp.patient_id = appt.patient_utilizador_id
                LEFT JOIN hospitalization hosp ON topp.patient_id = hosp.patient_utilizador_id 
                GROUP BY util.name_, topp.total_paid 
                ORDER BY topp.total_paid DESC; 
            
    
        """
        cur.execute(query)
        rows = cur.fetchall()



    except(Exception, psycopg2.Error) as error:
        cur.execute("ROLLBACK;")
        if(conn):
            glb.logger.error("Failed to list top 3 patients: ", error)
            print("Failed to list top 3 patients: ", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }
        return flask.jsonify(response)
    
    else:
        glb.logger.info("Top 3 patients listed successfully")
        response = {
            'status': glb.StatusCodes['success'],
            'results': [{'patient_name': row[0], 'amount_spent': row[1], 'procedures': row[2]} for row in rows]
        }
        cur.execute("COMMIT;")
        return flask.jsonify(response)

    finally:
        if(conn):
            cur.close()
            conn.close()


def daily_report(year, month, day):
    glb.logger.info(('GET /daily/' + str(year) + '-' + str(month) + '-' + str(day) ))
    conn = glb.db_connection()
    cur = conn.cursor()
    claims = get_jwt()
    year = int(year)
    month = int(month)
    day = int(day)
    if claims['role'] != 'assistant':
        return flask.jsonify({'error': 'Unauthorized'}), 401
    try:
        cur.execute("BEGIN;")
        cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
        cur.execute("LOCK TABLE surgery IN SHARE MODE;")
        cur.execute("LOCK TABLE prescription IN SHARE MODE;")
        cur.execute("LOCK TABLE payment IN SHARE MODE;")
       
        payment_sum = 0
        surgery_count = 0
        prescription_count = 0

        # list all payments, surgeries, and prescriptions made in the day
        query = """
        SELECT 
            (SELECT COALESCE(SUM(amount), 0) FROM payment WHERE date_payment = %s) as payment_sum,
            (SELECT COUNT(*) FROM surgery WHERE surgery_date = %s) as surgery_count,
            (SELECT COUNT(*) FROM prescription WHERE validity = %s) as prescription_count;
        """
        cur.execute(query, (datetime.date(year, month, day), datetime.date(year, month, day), datetime.date(year, month, day)))
        row = cur.fetchone()

        payment_sum = row[0]
        surgery_count = row[1]
        prescription_count = row[2]

        print(payment_sum, surgery_count, prescription_count)



    except(Exception, psycopg2.Error) as error:
        cur.execute("ROLLBACK;")
        if(conn):
            glb.logger.error("Failed to list daily report: ", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }
        return flask.jsonify(response)
    

    else:
        cur.execute("COMMIT;")
        # results: { amount_spent, surgeries, prescriptions }
        glb.logger.info("Daily report listed successfully")
        response = {
            'status': glb.StatusCodes['success'],
            'results': {
                'amount_spent': payment_sum,
                'surgeries': surgery_count,
                'prescriptions': prescription_count
            }
        }
        return flask.jsonify(response)


    finally:
        if(conn):
            cur.close()
            conn.close()


def monthly_report():
    #Get a list of the doctors with more surgeries each month in the last 12 months.
    glb.logger.info('GET /report')
    conn = glb.db_connection()

    cur = conn.cursor()
    claims = get_jwt()
    if claims['role'] != 'assistant':
        return flask.jsonify({'error': 'Unauthorized'}), 401
    
    try:
        cur.execute("BEGIN;")
        cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
        cur.execute("LOCK TABLE doctor IN SHARE MODE;")
        cur.execute("LOCK TABLE surgery IN SHARE MODE;")

        # get the doctor with most surgeries on each month of the last year
        query = """
        WITH months AS (
            SELECT to_char( date_trunc( 'month',
                                        CURRENT_DATE - (interval '1 month' * generate_series(0, 11)) ),
                            'Month' )
                AS month_name
            ),
        
        top_surgeries AS (
            SELECT doctor_employee_utilizador_id, 
                   COUNT(*) AS surgery_count,
                   TO_CHAR(surgery_date, 'Month') AS month,
                   RANK() OVER (PARTITION BY TO_CHAR(surgery_date, 'Month') ORDER BY COUNT(*) DESC, doctor_employee_utilizador_id ASC) AS rank
            FROM surgery
            JOIN doctor ON doctor_employee_utilizador_id = doctor.employee_utilizador_id
            WHERE EXTRACT(MONTH FROM surgery_date) >= EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 year')
            GROUP BY doctor_employee_utilizador_id, month
            )
        
        SELECT months.month_name,
               COALESCE(top_surgeries.doctor_employee_utilizador_id, 0) AS doctor_id,
               COALESCE(top_surgeries.surgery_count, 0) AS surgery_count
        FROM months
        LEFT JOIN top_surgeries ON months.month_name = top_surgeries.month AND top_surgeries.rank = 1
        ORDER BY TO_DATE(months.month_name, 'Month');
        """

        cur.execute(query)
        rows = cur.fetchall()
        print(rows)



    except(Exception, psycopg2.Error) as error:
        cur.execute("ROLLBACK;")
        if(conn):
            glb.logger.error("Failed to list doctors with most surgeries: ", error)
            print("Failed to list doctors with most surgeries: ", error)
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': f'Internal error: {error}'
        }
        return flask.jsonify(response)
    

    else:
        cur.execute("COMMIT;")
        # results: doctor_name and surgery_count
        glb.logger.info("Report fabricated successfully")
        response = {
            'status': glb.StatusCodes['success'],
            'results': [{'month' : rows[i][0], 'doctor_name': rows[i][1], 'surgery_count': rows[i][2]} for i in range(len(rows))]
        }
        return flask.jsonify(response)
    

    finally:
        if(conn):
            cur.close()
            conn.close()
    
