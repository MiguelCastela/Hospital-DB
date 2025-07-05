import flask
import logging
import jwt
import psycopg2
import datetime
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, JWTManager, get_jwt_identity, get_jwt
import funções_globais as glb

#Pra fazer a marcação de consultas é necessário verificar a disponibilidade do médico e das enfermeiras
#temos de utilizar locks para evitar problemas de concorrência

#VER: como restringir os endpoints a certos tipos de utilizadores?

#get_jwt_identity() retorna o id do utilizador que fez o pedido (token?)



# verificar se a data da cirugia está dentro do intervalo da hospitalização
def check_surgery_date(cur, hospitalization_id, surgery_date):
    cur.execute("""
                SELECT *
                FROM hospitalization
                WHERE hospitalization_id = %s AND %s BETWEEN start_date AND end_date
                """, (hospitalization_id, surgery_date))
    if cur.fetchone() is None:
        return False
    return True

#se o numero de consultas para aquele medico naquela data for maior que 0, o médico não está disponível
#ver o doctor tem alguma consulta
def doctor_check_appt(cur, doctor_id, date):
    cur.execute(""" 
                SELECT 
                    CASE
                        WHEN COUNT(*)>5 THEN 'Doctor is not available on the selected date'
                        ELSE 'Doctor is available on the selected date'
                    END AS availability
                FROM appointment
                WHERE doctor_employee_utilizador_id = %s AND appointment_date = %s;
                """, (doctor_id, date))
    return cur.fetchone()


#ver o doctor tem alguma cirurgia
def doctor_check_surgery(cur, doctor_id, date):
    cur.execute(""" 
                SELECT 
                    CASE
                        WHEN count(*)>0 THEN 'Doctor is not available on the selected date'
                        ELSE 'Doctor is available on the selected date'
                    END AS availability
                FROM surgery
                WHERE doctor_employee_utilizador_id = %s AND surgery_date = %s;
                """, (doctor_id, date))
    return cur.fetchone()


#verifica se o médico está disponível na data escolhida em termos de cirurgias e consultas
def check_doctor_availability(cur, doctor_id, date):
    doctor_appt = doctor_check_appt(cur, doctor_id, date)
    doctor_surgery = doctor_check_surgery(cur, doctor_id, date)
    if doctor_appt[0] == 'Doctor is not available on the selected date' or doctor_surgery[0] == 'Doctor is not available on the selected date':
        return False
    return True


#verificar se as nurses estão disponíveis
def check_nurse_availability(cur, nurse_id, date):
    nurse_appt = check_nurse_availability_appointment(cur, nurse_id, date)
    nurse_surgery = check_nurse_availability_surgery(cur, nurse_id, date)
    if nurse_appt == False or nurse_surgery == False:
        return False


#disponibilidade de enfermeiras para cirurgias
def check_nurse_availability_surgery(cur, nurse_id, date):
    cur.execute(""" 
                SELECT 
                    CASE
                        WHEN count(*)>0 THEN 'Nurse is not available on the selected date'
                        ELSE 'Nurse is available on the selected date'
                    END AS availability
                FROM enrolment_surgery
                JOIN surgery ON enrolment_surgery.surgery_id_surgery = surgery.id_surgery
                WHERE enrolment_surgery.nurse_employee_utilizador_id = %s AND surgery.surgery_date = %s;
                """, (nurse_id, date))
    result =  cur.fetchone()
    if result[0] == 'Nurse is not available on the selected date':
        return False
    return True


#disponibilidade de enfermeiras para consultas
def check_nurse_availability_appointment(cur, nurse_id, date):
    cur.execute(""" 
                SELECT 
                    CASE
                        WHEN count(*)>5 THEN 'Nurse is not available on the selected date'
                        ELSE 'Nurse is available on the selected date'
                    END AS availability
                FROM enrolment_appointment
                JOIN appointment ON enrolment_appointment.appointment_appointment_id = appointment.appointment_id
                WHERE enrolment_appointment.nurse_employee_utilizador_id = %s AND appointment.appointment_date = %s;
                """, (nurse_id, date))
    result =  cur.fetchone()
    if result[0] == 'Nurse is not available on the selected date':
        return False
    return True    


#verificar se as nurses têm os campos necessários
def check_nurse_fields(nurses):
    for nurse in nurses:
        if 'nurse_id' not in nurse or 'role_' not in nurse:
            return False
    return True

#adicionar tambem uma bill quando criar a consulta -- feito por triggers
#appointment shedule
def schedule_appointment():
    data = flask.request.json
    glb.logger.info(f'Received data: {data}')  # Log the received data
    
    if get_jwt():
        print(get_jwt())
    else:
        print("no token")


    #vai buscar o token ativo no momento
    id_patient = get_jwt_identity()
    claims = get_jwt()
    #verificar se o utilizador é um paciente
    if claims['role'] != 'patient':
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Unauthorized access'})

    conn = glb.db_connection()
    cur = conn.cursor()

    # verify that data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['doctor_id', 'date', 'type_type_'])
    if len(missing) > 0:
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': f'Missing fields: {", ".join(missing)}'})


    try:
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE appointment IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE enrolment_appointment IN ACCESS EXCLUSIVE MODE;")

        #fazemos assim porque caso o campo esteja vazio ele retorna uma lista vazia
        nurses = data.get('nurses', [])

        #verificar se o médico está disponível
        if check_doctor_availability(cur, data['doctor_id'], data['date']) == False:
            return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Doctor is not available on the selected date'})
        #criar a consulta

        #verify that type_type_ exists in table type_
        cur.execute("""
                    SELECT type_ FROM type_ WHERE type_ = %s;
                    """, (data['type_type_'],))
            
        if cur.fetchone() is None:   
            return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Type does not exist'})
            
        cur.execute("""
            insert into appointment (doctor_employee_utilizador_id, appointment_date, type_type_, patient_utilizador_id)
            values (%s, %s, %s, %s)
            RETURNING appointment_id
            """, (data['doctor_id'], data['date'], data['type_type_'], id_patient))
        appt_id = cur.fetchone()[0]
        
        #se houver nurses
        if(nurses != []):
            #verificar se as nurses têm os campos necessários
            if check_nurse_fields(nurses) == False:
                return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Nurses must have an id and a role_'})
            
            #verificar se as nurses estão disponíveis
            for nurse in nurses:
                if check_nurse_availability(cur, nurse['nurse_id'], data['date']) == False:
                    return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Nurse is not available on the selected date'})
                
            #adicionar as nurses à consulta
            for nurse in nurses:
                cur.execute("""
                            SELECT role_id FROM role_ WHERE role_name = %s;
                            """, (nurse['role_'],))
                role_id = cur.fetchone()
                if role_id is None:
                    return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Role not found'})
                cur.execute("""
                            insert into enrolment_appointment (role_role_id, appointment_appointment_id, nurse_employee_utilizador_id)
                            values (%s, %s, %s)
                            """, (role_id, appt_id, nurse['nurse_id'])
                            )
            
    except(Exception, psycopg2.DatabaseError) as error:
        glb.logger.error(f'POST /dbproj/appointment - error: {error}')
        glb.logger.error(f'POST /dbproj/appointment - data: {data}')  # Log the data when an error occurs
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': str(error)
        }
        #fazemos rollback para não guardar nada na base de dados caso haja um erro
        cur.execute("ROLLBACK;")

    else:
        #commit para guardar na base de dados
        cur.execute("COMMIT;")
        response = {
            'status': glb.StatusCodes['success'],
            'results': f'appointment_id: {appt_id}'
        }

    finally:
        if cur is not None:
            cur.close()
        
    return flask.jsonify(response)

#função para ver appointments de um paciente especifico
def see_appt_patient(patient_id):
    #o id de entrada serve para as assistentes poderem ver as consultas de um paciente especifico
    #basta modificar o codigo para fazer a verificação do id do token e do id de entrada
    id_cliente = get_jwt_identity()
    claims = get_jwt()


    #se for um assistente ou um paciente
    if claims['role']!='assistant' and (claims['role'] != 'patient' or id_cliente != patient_id):
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Unauthorized access'})

    conn = glb.db_connection()
    cur = conn.cursor()

    try:
        cur.execute("BEGIN;")
        cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
        cur.execute("""
                    SELECT *
                    FROM appointment
                    WHERE patient_utilizador_id = %s
                    """, (patient_id,))


    except(Exception, psycopg2.DatabaseError) as error:
        cur.execute("ROLLBACK;")
        glb.logger.error(f'GET /dbproj/appointment - error: {error}')
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': str(error)
        }
        return flask.jsonify(response)


    else:
        response = {
            'status': glb.StatusCodes['success'],
            "1º-> appointment_id; 2->date, 3->billing_id , 4->doctor_id, 5->patient_id :"
            'results': cur.fetchall() 
        }
        cur.execute("COMMIT;")
        return flask.jsonify(response)


    finally:
        if cur is not None:
            cur.close()

# ------ surgery and hospitalization ----
#verificar se as nurses estão disponíveis


#ver se o id de hospitalização ja exite ou não
def check_hospitalization_id(cur, hospitalization_id):
    cur.execute("""
                SELECT *
                FROM hospitalization
                WHERE hospitalization_id = %s
                """, (hospitalization_id,))
    if cur.fetchone() is None:
        return False
    return True

#hospitalização leva a uma cirurgia?
#possibilidade de inserir varias nurses e depois temos de inserir os role_s por nurse

#se a hospitalização não existir, criar uma nova senão, adicionar a cirurgia à hospitalização
#surgery shedule
def schedule_surgery_existing_hosp(hospitalization_id):
    claims = get_jwt()
    #se for um assistente
    if claims['role'] != 'assistant':
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Unauthorized access'})

    data = flask.request.json
    conn = glb.db_connection()
    cur = conn.cursor()


    # verify that data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['doctor', 'date', 'type_surgery', 'duration', 'nurses', 'patient_id'])
    if len(missing) > 0:
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': f'Missing fields: {", ".join(missing)}'})


    #verificar se a hospitalização existe
    if check_hospitalization_id(cur, hospitalization_id) == False:
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Hospitalization not found'})

    if check_surgery_date(cur, hospitalization_id, data['date']) == False:
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Surgery date is not within the hospitalization period'})
    
    try:
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE surgery IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE hospitalization IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE enrolment_surgery IN ACCESS EXCLUSIVE MODE;")
        nurses = data['nurses']

        #verificar se as nurses têm os campos necessários
        if check_nurse_fields(nurses) == False:
            return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Nurses must have an id and a role_'})
        
        #verificar se as nurses estão disponíveis
        for nurse in nurses:
            print(nurses)
            if check_nurse_availability(cur, nurse['nurse_id'], data['date']) == False:
                return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Nurse is not available on the selected date'})

        #ver se o médico está disponível
        if check_doctor_availability(cur, data['doctor'], data['date']) == False:
            return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Doctor is not available on the selected date'})
        
        #criar a cirurgia
        cur.execute("""
                INSERT INTO surgery (type_, surgery_date, surgery_duration, doctor_employee_utilizador_id, hospitalization_hospitalization_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_surgery
                """, (data['type_surgery'], data['date'], data['duration'], data['doctor'], hospitalization_id))
        surgery_id = cur.fetchone()[0]

        #adicionar as nurses à cirurgia
        print(nurses)
        for nurse in nurses:
            cur.execute("""
                        SELECT role_id FROM role_ WHERE role_name = %s;
                        """, (nurse['role_'],))
            role_id = cur.fetchone()
            if role_id is None:
                return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Role not found'})

            cur.execute("""
                        INSERT INTO enrolment_surgery (role_role_id, surgery_id_surgery, nurse_employee_utilizador_id)
                        VALUES (%s, %s, %s)
                        """, (role_id, surgery_id, nurse['nurse_id']))


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
            'results': {
                'surgery_id': surgery_id,
                'patient_id': data['patient_id'],
                'doctor': data['doctor'],
                'date': data['date'],
                'type_': data['type_surgery'],
                'duration': data['duration'],
                'nurses': data['nurses']
            }
        }
        cur.execute("COMMIT;")
        return flask.jsonify(response)
    finally:

        if cur is not None:
            cur.close()
        


def schedule_surgery_new_hosp():
    claims = get_jwt()
    #se for um assistente
    if claims['role'] != 'assistant':
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Unauthorized access'})
    data = flask.request.json

    conn = glb.db_connection()
    cur = conn.cursor()

    # verify that data contains all the necessary fields
    missing = glb.check_missingfirelds(data, ['doctor', 'room', 'type_', 'start_date', 'end_date', 'nurses', 'patient_id'])
    if len(missing) > 0:
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': f'Missing fields: {", ".join(missing)}'})
    
    if data['start_date'] > data['date'] or data['end_date'] < data['date']:
        return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Surgery date is not within the hospitalization period'})        

    try:
        cur.execute("BEGIN;")
        cur.execute("LOCK TABLE surgery IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE hospitalization IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE role_ IN ACCESS EXCLUSIVE MODE;")
        cur.execute("LOCK TABLE enrolment_surgery IN ACCESS EXCLUSIVE MODE;")

        #temos de ter pelo menos uma infermeira para a cirurgia
        nurses = data['nurses']

        #verificar se as nurses têm os campos necessários
        if check_nurse_fields(nurses) == False:
            return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Nurses must have an id and a role_'})

        #verificar se as nurses estão disponíveis
        for nurse in nurses:
            if check_nurse_availability(cur, nurse['nurse_id'], data['date']) == False:
                return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Nurse is not available on the selected date'})

        #ver se o médico está disponível
        if check_doctor_availability(cur, data['doctor'], data['date']) == False:
            return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Doctor is not available on the selected date'})
        

        #criar a hospitalização
        #nurse_id é o id do enfermeiro que está responsavel
        cur.execute("""
                    INSERT INTO hospitalization (room, type_,start_date, end_date, nurse_employee_utilizador_id, patient_utilizador_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING hospitalization_id
                    """, (data['room'], data['type_'], data['start_date'], data['end_date'], data['nurse_id'], data['patient_id']))
        hospitalization_id = cur.fetchone()[0]

        #criar a cirurgia
        cur.execute("""
                INSERT INTO surgery (type_, surgery_date, surgery_duration, doctor_employee_utilizador_id, hospitalization_hospitalization_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_surgery
                """, (data['type_'], data['date'], data['duration'], data['doctor'], hospitalization_id))
        surgery_id = cur.fetchone()[0]

        #adicionar as nurses à cirurgia
        for nurse in nurses:
            print(nurse["role_"])
            cur.execute("""
                        SELECT role_id FROM role_ WHERE role_name = %s;
                        """, (nurse['role_'],))
            role_id = cur.fetchone()
            print(role_id)
            if role_id is None:
                return flask.jsonify({'status': glb.StatusCodes['api_error'], 'errors': 'Role not found'})
            cur.execute("""
                        INSERT INTO enrolment_surgery (role_role_id, surgery_id_surgery, nurse_employee_utilizador_id)
                        VALUES (%s, %s, %s)
                        """, (role_id, surgery_id, nurse['nurse_id']))
    

    except(Exception, psycopg2.DatabaseError) as error:
        glb.logger.error(f'POST /dbproj/surgery - error: {error}')
        response = {
            'status': glb.StatusCodes['internal_error'],
            'errors': str(error)
        }
        cur.execute("ROLLBACK;")


    else:
        response = {
            'status': glb.StatusCodes['success'],
            'results': {
                'hospitalization_id': hospitalization_id,
                'surgery_id': surgery_id,
                'patient_id': data['patient_id'],
                'doctor': data['doctor'],
                'date': data['date'],
                'type_': data['type_'],
                'duration': data['duration'],
                'nurses': data['nurses']
            }
        }
        cur.execute("COMMIT;")
        return flask.jsonify(response)


    finally:
        if cur is not None:
            cur.close()
    


    