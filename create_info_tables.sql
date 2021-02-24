DROP TABLE IF EXISTS raw_to_clean_medicine;
DROP TABLE IF EXISTS clean_medicine_to_dosage;
DROP TABLE IF EXISTS medicine_purpose;
DROP TABLE IF EXISTS protocol_step_definition;



CREATE TABLE raw_to_clean_medicine (
	raw_name VARCHAR,
	raw_dosage VARCHAR,
	rxcui INTEGER,
	PRIMARY KEY (raw_name, raw_dosage)
	
);

CREATE TABLE clean_medicine_to_dosage (
	id serial PRIMARY KEY,
	rxcui INTEGER ,
	medicine VARCHAR,
	dosage float
);

CREATE TABLE medicine_purpose (
	name VARCHAR PRIMARY KEY,
	hypertension BOOL,
	diabetes BOOL
);

CREATE TABLE protocol_step_definition (
	id serial PRIMARY KEY,
	protocol_id UUID,
	step INTEGER,
	amlodipine FLOAT,
	telmisartan FLOAT,
	losartan FLOAT,
	atenolol FLOAT,
	enalapril FLOAT,
	chlorthalidone FLOAT,
	hydrochlorothiazide FLOAT,
	other_bp_medications FLOAT
);


COPY raw_to_clean_medicine(raw_name, raw_dosage, rxcui)
	FROM '/PATH/simple-etl/informational_tables/raw_to_clean_medicine.csv'
	DELIMITER ','
	CSV HEADER;


COPY clean_medicine_to_dosage(rxcui, medicine, dosage)
	FROM '/PATH/simple-etl/informational_tables/clean_medicine_to_dosage.csv'
	DELIMITER ','
	CSV HEADER;


COPY medicine_purpose(name, hypertension, diabetes)
	FROM '/PATH/simple_etl/informational_tables/medicine_purpose.csv'
	DELIMITER ','
	CSV HEADER;


COPY protocol_step_definition (protocol_id, 
				step, 
				amlodipine,
				telmisartan,
				losartan,
				atenolol,
				enalapril,
				chlorthalidone,
				hydrochlorothiazide,
				other_bp_medications
	)
	FROM '/PATH/simple-etl/informational_tables/protocol_step_definition.csv'
	DELIMITER ','
	CSV HEADER;
