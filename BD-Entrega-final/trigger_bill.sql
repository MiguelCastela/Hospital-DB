-- Define appointment billing trigger
CREATE OR REPLACE FUNCTION create_app_billing_trigger() 
RETURNS TRIGGER AS $$
BEGIN
    -- Insert a new billing with default values
    INSERT INTO billing (cost, already_paid) 
    VALUES (50, 0) RETURNING bill_id 
    INTO NEW.billing_bill_id;

    -- Update the appointment with the new billing id
    UPDATE appointment 
    SET billing_bill_id = NEW.billing_bill_id 
    WHERE appointment_id = NEW.appointment_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add the trigger to the appointment table
CREATE OR REPLACE TRIGGER appointment_before_insert
BEFORE INSERT ON appointment
FOR EACH ROW
EXECUTE FUNCTION create_app_billing_trigger();



-- Define hospitalization billing trigger
CREATE OR REPLACE FUNCTION create_hosp_billing_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert a new billing with default values
    -- Currently empty, as it will be updated by the surgery trigger
    INSERT INTO billing (cost, already_paid) 
    VALUES (0, 0) RETURNING bill_id 
    INTO NEW.billing_bill_id;

    -- Update the hospitalization with the new billing id
    UPDATE hospitalization 
    SET billing_bill_id = NEW.billing_bill_id 
    WHERE hospitalization_id = NEW.hospitalization_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add the trigger to the hospitalization table
CREATE OR REPLACE TRIGGER hospitalization_before_insert
BEFORE INSERT ON hospitalization
FOR EACH ROW
EXECUTE FUNCTION create_hosp_billing_trigger();




-- Define surgery billing trigger
CREATE OR REPLACE FUNCTION update_surg_billing_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Update associated billing with surgery cost
    UPDATE billing
    SET cost = cost + 100
    WHERE bill_id = (
        SELECT billing_bill_id
        FROM hospitalization
        WHERE hospitalization_id = NEW.hospitalization_hospitalization_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add the trigger to the surgery table
CREATE OR REPLACE TRIGGER surgery_after_insert
AFTER INSERT ON surgery
FOR EACH ROW
EXECUTE FUNCTION update_surg_billing_trigger();




-- Define a payment trigger
CREATE OR REPLACE FUNCTION update_billing_payment_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the billing with the new payment
    UPDATE billing
    SET already_paid = billing.already_paid + NEW.amount
    WHERE bill_id = NEW.billing_bill_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add the trigger to the payment table
CREATE OR REPLACE TRIGGER payment_after_insert
AFTER INSERT ON payment
FOR EACH ROW
EXECUTE FUNCTION update_billing_payment_trigger();