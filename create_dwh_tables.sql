DROP TABLE IF EXISTS  blood_pressure_observations_over_time;
DROP TABLE IF EXISTS  encounters_over_time;
DROP TABLE IF EXISTS  patient_states_over_time;
DROP TABLE IF EXISTS  medicine_over_time;
DROP TABLE IF EXISTS  protocol_steps_over_time;
DROP TABLE IF EXISTS  visit_counts_over_time;

CREATE TABLE blood_pressure_observations_over_time (
	id serial PRIMARY KEY,
	patient_id UUID NOT NULL,
	months_since_registration INTEGER,
	calendar_month DATE,
	systolic INTEGER,
	diastolic INTEGER,
	months_since_bp_observation INTEGER
);


CREATE TABLE encounters_over_time (
	id serial PRIMARY KEY,
	patient_id UUID NOT NULL,
	calendar_month DATE,
	months_since_registration INTEGER,
	months_since_encounter INTEGER
);


CREATE TABLE patient_states_over_time (
	id serial PRIMARY KEY,
	patient_id UUID NOT NULL,
	calendar_month DATE,
	months_since_registration INTEGER,
	diagnosed_disease_state VARCHAR,
	protocol_state VARCHAR,
	treatment_state VARCHAR,
	bp_observation_state VARCHAR,
	assigned_facility UUID
);

CREATE TABLE medicine_over_time (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    calendar_month DATE,
    months_since_registration INTEGER,
    amlodipine FLOAT,
    telmisartan FLOAT,
    losartan FLOAT,
    atenolol FLOAT,
    enalapril FLOAT,
    chlorthalidone FLOAT,
    hydrochlorothiazide FLOAT,
    other_bp_medications FLOAT
);

CREATE TABLE protocol_steps_over_time (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    protocol_id UUID,
    calendar_month DATE,
    months_since_registration INTEGER,
    step INTEGER
);


CREATE TABLE visit_counts_over_time (
    id serial PRIMARY KEY,
    patient_id UUID NOT NULL,
    calendar_month DATE,
    months_since_registration INTEGER,
    encounters INTEGER,
    bp_observations INTEGER
);