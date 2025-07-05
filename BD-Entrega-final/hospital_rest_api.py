import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager, jwt_required
import registers
import logins
import hospital_stats
import appointments_and_surgeries
import prescriptions
import funções_globais as glb
import payment
from datetime import timedelta


class config:
    JWT_SECRET_KEY = '1234'
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes = 30)
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_CSRF_PROTECT = False

app = flask.Flask(__name__)
app.config.from_object(config)
jwt = JWTManager(app)





StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

#DATABASE ACCESS

'''
def db_connection():
    db = psycopg2.connect(
        user='aulaspl',
        password='aulaspl',
        host='127.0.0.1',
        port='5432',
        database='projeto'
    )

    return db
'''
#ENDPOINTS
@app.route('/')
def landing_page():
    return """
   OLAAAAAAAAAAAAAA  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2023-2024 Team<br/>
    <br/>
    """

@app.route('/dbproj/register/patient', methods=['POST'])
def add_patient_endpoint():
    return registers.add_patient()

@app.route('/dbproj/register/assistant', methods=['POST'])
def add_assistant_endpoint():
    return registers.add_assistant()

@app.route('/dbproj/register/nurse', methods=['POST'])
def add_nurse_endpoint():
    return registers.add_nurse()

@app.route('/dbproj/register/doctor', methods=['POST'])
def add_doctor_endpoint():
    return registers.add_doctor()

@app.route('/dbproj/utilizador', methods=['POST'])
def login():
    return logins.authenticate_user()

@app.route('/dbproj/appointment', methods=['POST'])
@jwt_required()
def add_appointment():
    return appointments_and_surgeries.schedule_appointment()

@app.route('/dbproj/appointments/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_appointments(patient_id):
    return appointments_and_surgeries.see_appt_patient(patient_id)

@app.route('/dbproj/surgery', methods=['POST'])
@jwt_required()
def add_surgery():
    return appointments_and_surgeries.schedule_surgery_new_hosp()

@app.route('/dbproj/surgery/<int:hospitalization_id>', methods=['POST'])
@jwt_required()
def schedule_surgery_existing_hosp(hospitalization_id):
    return appointments_and_surgeries.schedule_surgery_existing_hosp(hospitalization_id)

@app.route('/dbproj/prescription', methods=['POST'])
@jwt_required()
def add_prescription():
    return prescriptions.add_prescription()

@app.route('/dbproj/prescriptions/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_prescriptions(patient_id):
    return prescriptions.get_prescriptions(patient_id)

@app.route('/dbproj/bills/<int:bill_id>', methods=['POST'])
@jwt_required()
def pay_bill(bill_id):
    return payment.execute_payment(bill_id)

@app.route('/dbproj/top3', methods=['GET'])
@jwt_required()
def top3():
    return hospital_stats.list_top3()

@app.route('/dbproj/daily/<date_str>', methods=['GET'])
@jwt_required()
def daily_stats(date_str):
    # break the date string into year, month, day
    year, month, day = date_str.split('-')
    return hospital_stats.daily_report(year, month, day)

@app.route('/dbproj/report', methods=['GET'])
@jwt_required()
def report():
    return hospital_stats.monthly_report()

if __name__ == '__main__':

    # set up logging
    logging.basicConfig(filename='log_file.log')
    glb.logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    glb.logger.addHandler(ch)

    '''
    with open('drop_every_table.sql', 'r') as f:
        conn = glb.db_connection()
        cur = conn.cursor()
        cur.execute(f.read())
        conn.commit()
        conn.close()
    
    with open('criacao_tabelas.sql', 'r') as f:
        conn = glb.db_connection()
        cur = conn.cursor()
        cur.execute(f.read())
        conn.commit()
        conn.close()

    #triggers a seguir á criação das tabelas
    with open('trigger_bill.sql', 'r') as f:
        conn = glb.db_connection()
        cur = conn.cursor()
        cur.execute(f.read())
        conn.commit()
        conn.close()
    '''

    host = '127.0.0.1'
    port = 8080
    glb.logger.info(f'API v1.0 online: http://{host}:{port}')
    app.run(host=host, threaded=True, port=port)
    
