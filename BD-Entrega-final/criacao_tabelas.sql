CREATE TABLE patient (
	utilizador_id BIGINT NOT NULL,
	PRIMARY KEY(utilizador_id)
);

CREATE TABLE employee (
	utilizador_id BIGINT NOT NULL,
	PRIMARY KEY(utilizador_id)
);

CREATE TABLE doctor (
	medical_license_id	BIGINT NULL,
	university		 VARCHAR(512) NOT NULL,
	specialization_expertise VARCHAR(512) NOT NULL,
	employee_utilizador_id	 BIGINT NOT NULL,
	PRIMARY KEY(employee_utilizador_id)
);

CREATE TABLE nurse (
	category_category_name VARCHAR(512) NOT NULL,
	employee_utilizador_id BIGINT NOT NULL,
	PRIMARY KEY(employee_utilizador_id)
);

CREATE TABLE assistant (
	employee_utilizador_id BIGINT NOT NULL,
	PRIMARY KEY(employee_utilizador_id)
);

CREATE TABLE appointment (
	appointment_id		 BIGSERIAL NOT NULL,
	appointment_date		 TIMESTAMP NOT NULL,
	type_type_			 VARCHAR(512) NOT NULL,
	billing_bill_id		 BIGINT NOT NULL,
	doctor_employee_utilizador_id BIGINT NOT NULL,
	patient_utilizador_id	 BIGINT NOT NULL,
	PRIMARY KEY(appointment_id)
);

CREATE TABLE surgery (
	id_surgery				 BIGSERIAL NOT NULL,
	type_				 VARCHAR(512) NOT NULL,
	surgery_date			 TIMESTAMP NOT NULL,
	surgery_duration			 FLOAT(8) NOT NULL,
	doctor_employee_utilizador_id	 BIGINT NOT NULL,
	hospitalization_hospitalization_id BIGINT NOT NULL,
	PRIMARY KEY(id_surgery)
);

CREATE TABLE hospitalization (
	hospitalization_id		 BIGSERIAL NOT NULL,
	room			 INTEGER NOT NULL,
	type_			 VARCHAR(512) NOT NULL,
	start_date			 DATE NOT NULL,
	end_date			 DATE NOT NULL,
	billing_bill_id		 BIGINT NOT NULL,
	nurse_employee_utilizador_id BIGINT NOT NULL,
	patient_utilizador_id	 BIGINT NOT NULL,
	PRIMARY KEY(hospitalization_id)
);

CREATE TABLE prescription (
    id_prescription             BIGSERIAL NOT NULL,
    hospitalization_hospitalization_id BIGINT,
    appointment_appointment_id         BIGINT,
    validity                 DATE NOT NULL,
    PRIMARY KEY(id_prescription)
);

CREATE TABLE medication (
	medication_name VARCHAR(512) NOT NULL,
	medication_id	 BIGSERIAL NOT NULL,
	PRIMARY KEY(medication_id)
);
INSERT INTO medication (medication_name, medication_id) VALUES ('paracetamol', 1);
INSERT INTO medication (medication_name, medication_id) VALUES ('ibuprofeno', 2);
INSERT INTO medication (medication_name, medication_id) VALUES ('aspirina', 3);
INSERT INTO medication (medication_name, medication_id) VALUES ('dorflex', 4);

CREATE TABLE sideeffect (
	side_effect_id BIGSERIAL NOT NULL,
	symptoms	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(side_effect_id)
);
INSERT INTO sideeffect (symptoms) VALUES ('dor de cabeca');
INSERT INTO sideeffect (symptoms) VALUES ('dor de barriga');
INSERT INTO sideeffect (symptoms) VALUES ('dor de costas');
INSERT INTO sideeffect (symptoms) VALUES ('ataque cardiaco');

CREATE TABLE billing (
	cost	 NUMERIC(10,2) NOT NULL,
	bill_id BIGSERIAL NOT NULL,
	already_paid NUMERIC(10,2) NOT NULL,
	PRIMARY KEY(bill_id)
);

CREATE TABLE payment (
    payment_id     BIGSERIAL NOT NULL,
    date_payment     DATE NOT NULL,
    num_payment     BIGSERIAL NOT NULL,
    amount         NUMERIC(10,2) NOT NULL,
    billing_bill_id BIGINT NOT NULL,
	method 	   VARCHAR(512) NOT NULL,
    PRIMARY KEY(payment_id)
);


CREATE TABLE specialization (
	expertise		 VARCHAR(512) NOT NULL,
	specialization_expertise VARCHAR(512),
	PRIMARY KEY(expertise)
);
INSERT INTO specialization (expertise) VALUES ('cardiologia');
INSERT INTO specialization (expertise) VALUES ('neurologia');
INSERT INTO specialization (expertise) VALUES ('ortopedia');

CREATE TABLE effect_property (
	occurences		 FLOAT(8) NOT NULL,
	severety			 FLOAT(8) NOT NULL,
	sideeffect_side_effect_id BIGINT NOT NULL,
	medication_medication_id	 BIGINT NOT NULL,
	PRIMARY KEY(sideeffect_side_effect_id,medication_medication_id)
);
INSERT INTO effect_property (occurences, severety, sideeffect_side_effect_id, medication_medication_id) VALUES (1, 1, 1, 1);
INSERT INTO effect_property (occurences, severety, sideeffect_side_effect_id, medication_medication_id) VALUES (2, 2, 2, 2);
INSERT INTO effect_property (occurences, severety, sideeffect_side_effect_id, medication_medication_id) VALUES (3, 3, 3, 3);
INSERT INTO effect_property (occurences, severety, sideeffect_side_effect_id, medication_medication_id) VALUES (4, 4, 4, 4);

CREATE TABLE contract_ (
	id_contract		 BIGSERIAL NOT NULL,
	start_date		 DATE NOT NULL,
	end_date		 DATE NOT NULL,
	employee_utilizador_id BIGINT NOT NULL,
	PRIMARY KEY(id_contract)
);

CREATE TABLE utilizador (
	birthday	 DATE NOT NULL,
	id_user_cc	 BIGINT NOT NULL,
	nationality VARCHAR(512) NOT NULL,
	name_	 VARCHAR(512) NOT NULL,
	password_	 VARCHAR(512) NOT NULL,
	mail	 VARCHAR(512) NOT NULL,
	id		 BIGSERIAL NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE role_ (
	role_id	 BIGSERIAL NOT NULL,
	role_name VARCHAR(512) NOT NULL,
	PRIMARY KEY(role_id)
);
INSERT INTO role_ (role_name) VALUES ('anasthesiologist');
INSERT INTO role_ (role_name) VALUES ('overseer');
INSERT INTO role_ (role_name) VALUES ('backup');

CREATE TABLE enrolment_surgery (
	role_role_id		 BIGINT NOT NULL,
	surgery_id_surgery		 BIGINT,
	nurse_employee_utilizador_id BIGINT,
	PRIMARY KEY(role_role_id,surgery_id_surgery,nurse_employee_utilizador_id)
);

CREATE TABLE enrolment_appointment (
	role_role_id		 BIGINT NOT NULL,
	appointment_appointment_id	 BIGINT NOT NULL,
	nurse_employee_utilizador_id BIGINT NOT NULL,
	PRIMARY KEY(role_role_id,appointment_appointment_id,nurse_employee_utilizador_id)
);

CREATE TABLE quantity (
    medication_ammount        INTEGER NOT NULL,
    frequency                INTEGER NOT NULL,
    medication_medication_id     BIGINT NOT NULL,
    prescription_id_prescription BIGINT NOT NULL,
    PRIMARY KEY(medication_medication_id,prescription_id_prescription)
);


CREATE TABLE type_ (
	type_ VARCHAR(512),
	PRIMARY KEY(type_)
);
INSERT INTO type_ (type_) VALUES ('oftalmologia');
INSERT INTO type_ (type_) VALUES ('cardiologia');
INSERT INTO type_ (type_) VALUES ('neurologia');
INSERT INTO type_ (type_) VALUES ('ortopedia');

CREATE TABLE category (
	category_name		 VARCHAR(512) NOT NULL,
	category_category_name VARCHAR(512),
	PRIMARY KEY(category_name)
);
INSERT INTO category (category_name) VALUES ('junior');
INSERT INTO category (category_name) VALUES ('senior');
INSERT INTO category (category_name) VALUES ('leader');

ALTER TABLE patient ADD CONSTRAINT patient_fk1 FOREIGN KEY (utilizador_id) REFERENCES utilizador(id);
ALTER TABLE employee ADD CONSTRAINT employee_fk1 FOREIGN KEY (utilizador_id) REFERENCES utilizador(id);
ALTER TABLE doctor ADD UNIQUE (medical_license_id);
ALTER TABLE doctor ADD CONSTRAINT doctor_fk1 FOREIGN KEY (specialization_expertise) REFERENCES specialization(expertise);
ALTER TABLE doctor ADD CONSTRAINT doctor_fk2 FOREIGN KEY (employee_utilizador_id) REFERENCES employee(utilizador_id);
ALTER TABLE doctor ADD CONSTRAINT constraint_1 CHECK (University ~ '^[a-zA-Z ]*$');
ALTER TABLE nurse ADD CONSTRAINT nurse_fk1 FOREIGN KEY (category_category_name) REFERENCES category(category_name);
ALTER TABLE nurse ADD CONSTRAINT nurse_fk2 FOREIGN KEY (employee_utilizador_id) REFERENCES employee(utilizador_id);
ALTER TABLE assistant ADD CONSTRAINT assistant_fk1 FOREIGN KEY (employee_utilizador_id) REFERENCES employee(utilizador_id);
ALTER TABLE appointment ADD UNIQUE (billing_bill_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk1 FOREIGN KEY (billing_bill_id) REFERENCES billing(bill_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk2 FOREIGN KEY (doctor_employee_utilizador_id) REFERENCES doctor(employee_utilizador_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk3 FOREIGN KEY (patient_utilizador_id) REFERENCES patient(utilizador_id);
ALTER TABLE appointment ADD CONSTRAINT constraint_2 CHECK (Appointment_Date IS NOT NULL AND Appointment_Date = CAST(Appointment_Date AS DATE));
ALTER TABLE surgery ADD CONSTRAINT surgery_fk1 FOREIGN KEY (doctor_employee_utilizador_id) REFERENCES doctor(employee_utilizador_id);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk2 FOREIGN KEY (hospitalization_hospitalization_id) REFERENCES hospitalization(hospitalization_id);
ALTER TABLE surgery ADD CONSTRAINT constraint_3 CHECK (type_ ~ '^[a-zA-Z ]*$');
ALTER TABLE surgery ADD CONSTRAINT constraint_4 CHECK (Surgery_date IS NOT NULL AND Surgery_date = CAST(Surgery_date AS DATE));
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk1 FOREIGN KEY (billing_bill_id) REFERENCES billing(bill_id);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk2 FOREIGN KEY (nurse_employee_utilizador_id) REFERENCES nurse(employee_utilizador_id);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk3 FOREIGN KEY (patient_utilizador_id) REFERENCES patient(utilizador_id);
ALTER TABLE hospitalization ADD CONSTRAINT constraint_5 CHECK (type_ ~ '^[a-zA-Z ]*$');
ALTER TABLE hospitalization ADD CONSTRAINT constraint_6 CHECK (Start_date < End_date);
ALTER TABLE prescription ADD CONSTRAINT prescription_fk1 FOREIGN KEY (hospitalization_hospitalization_id) REFERENCES hospitalization(hospitalization_id);
ALTER TABLE prescription ADD CONSTRAINT prescription_fk2 FOREIGN KEY (appointment_appointment_id) REFERENCES appointment(appointment_id);
ALTER TABLE medication ADD CONSTRAINT constraint_7 CHECK (Medication_name ~ '^[a-zA-Z ]*$');
ALTER TABLE sideeffect ADD UNIQUE (symptoms);
ALTER TABLE sideeffect ADD CONSTRAINT constraint_8 CHECK (Symptoms ~ '^[a-zA-Z ]*$');
ALTER TABLE payment ADD CONSTRAINT payment_fk1 FOREIGN KEY (billing_bill_id) REFERENCES billing(bill_id);
ALTER TABLE specialization ADD CONSTRAINT specialization_fk1 FOREIGN KEY (specialization_expertise) REFERENCES specialization(expertise);
ALTER TABLE specialization ADD CONSTRAINT constraint_9 CHECK (Expertise ~ '^[a-zA-Z0-9 ]*$');
ALTER TABLE effect_property ADD CONSTRAINT effect_property_fk1 FOREIGN KEY (sideeffect_side_effect_id) REFERENCES sideeffect(side_effect_id);
ALTER TABLE effect_property ADD CONSTRAINT effect_property_fk2 FOREIGN KEY (medication_medication_id) REFERENCES medication(medication_id);
ALTER TABLE contract_ ADD CONSTRAINT contract_fk1 FOREIGN KEY (employee_utilizador_id) REFERENCES employee(utilizador_id);
ALTER TABLE contract_ ADD CONSTRAINT constraint_10 CHECK (Start_Date < End_Date);
ALTER TABLE utilizador ADD UNIQUE (mail);
ALTER TABLE utilizador ADD CONSTRAINT constraint_11 CHECK (name_ ~ '^[a-zA-ZÀ-ÿ ]*$');
ALTER TABLE utilizador ADD CONSTRAINT constraint_12 CHECK (birthday < CURRENT_DATE);
ALTER TABLE utilizador ADD CONSTRAINT constraint_13 CHECK (password_ ~ '^[a-zA-Z0-9 ]*$');
ALTER TABLE utilizador ADD CONSTRAINT constraint_14 CHECK (mail LIKE '%' || '@' || '%');
ALTER TABLE utilizador ADD CONSTRAINT constraint_15 CHECK (LENGTH(CAST(ID_user_CC AS VARCHAR)) = 9);
ALTER TABLE role_ ADD UNIQUE (role_name);
ALTER TABLE role_ ADD CONSTRAINT constraint_16 CHECK (Role_name ~ '^[a-zA-Z ]*$');
ALTER TABLE enrolment_surgery ADD CONSTRAINT enrolment_surgery_fk1 FOREIGN KEY (role_role_id) REFERENCES role_(role_id);
ALTER TABLE enrolment_surgery ADD CONSTRAINT enrolment_surgery_fk2 FOREIGN KEY (surgery_id_surgery) REFERENCES surgery(id_surgery);
ALTER TABLE enrolment_surgery ADD CONSTRAINT enrolment_surgery_fk3 FOREIGN KEY (nurse_employee_utilizador_id) REFERENCES nurse(employee_utilizador_id);
ALTER TABLE enrolment_appointment ADD CONSTRAINT enrolment_appointment_fk1 FOREIGN KEY (role_role_id) REFERENCES role_(role_id);
ALTER TABLE enrolment_appointment ADD CONSTRAINT enrolment_appointment_fk2 FOREIGN KEY (appointment_appointment_id) REFERENCES appointment(appointment_id);
ALTER TABLE enrolment_appointment ADD CONSTRAINT enrolment_appointment_fk3 FOREIGN KEY (nurse_employee_utilizador_id) REFERENCES nurse(employee_utilizador_id);
ALTER TABLE quantity ADD CONSTRAINT quantity_fk1 FOREIGN KEY (medication_medication_id) REFERENCES medication(medication_id);
ALTER TABLE quantity ADD CONSTRAINT quantity_fk2 FOREIGN KEY (prescription_id_prescription) REFERENCES prescription(id_prescription);
ALTER TABLE type_ ADD CONSTRAINT constraint_17 CHECK (type_ ~ '^[a-zA-Z0-9 ]*$');
ALTER TABLE category ADD CONSTRAINT category_fk1 FOREIGN KEY (category_category_name) REFERENCES category(category_name);
ALTER TABLE category ADD CONSTRAINT constraint_18 CHECK (Category_name ~ '^[a-zA-Z ]*$');
ALTER TABLE payment ADD CONSTRAINT constraint_19 CHECK (Method IN ('check', 'credit card', 'debit card', 'paypal', 'mbway', 'money'));