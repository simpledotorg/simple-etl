from jinja2 import Template

dates = [
    '\'2018/01/31\'',
    '\'2018/02/28\'',
    '\'2018/03/31\'',
    '\'2018/04/30\'',
    '\'2018/05/31\'',
    '\'2018/06/30\'',
    '\'2018/07/31\'',
    '\'2018/08/31\'',
    '\'2018/09/30\'',
    '\'2018/10/31\'',
    '\'2018/11/30\'',
    '\'2018/12/31\'',
    '\'2019/01/31\'',
    '\'2019/02/28\'',
    '\'2019/03/31\'',
    '\'2019/04/30\'',
    '\'2019/05/31\'',
    '\'2019/06/30\'',
    '\'2019/07/31\'',
    '\'2019/08/31\'',
    '\'2019/09/30\'',
    '\'2019/10/31\'',
    '\'2019/11/30\'',
    '\'2019/12/31\'',
    '\'2020/01/31\'',
    '\'2020/02/29\'',
    '\'2020/03/31\'',
    '\'2020/04/30\'',
    '\'2020/05/31\'',
    '\'2020/06/30\'',
    '\'2020/07/31\'',
    '\'2020/08/31\'',
    '\'2020/09/30\'',
    '\'2020/10/31\'',
    '\'2020/11/30\'',
    '\'2020/12/31\''
]

bpoot_query = """
{% for date in dates %}
    INSERT INTO blood_pressure_observations_over_time(patient_id, 
                                                        systolic, 
                                                        diastolic, 
                                                        calendar_month, 
                                                        months_since_registration,
                                                        months_since_bp_observation)
    SELECT 
        blood_pressures.patient_id, 
        blood_pressures.systolic, 
        blood_pressures.diastolic,

        {{date}} 
            AS calendar_month, 

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', patients.recorded_at)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', patients.recorded_at)) 
            AS months_since_registration,

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', blood_pressures.recorded_at)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', blood_pressures.recorded_at)) 
            AS months_since_bp_observation


        FROM blood_pressures

        INNER JOIN
        (
            SELECT patient_id, max(recorded_at) as last_record
            FROM blood_pressures
            WHERE recorded_at::date <= {{date}}::date
            GROUP BY patient_id
        ) as latest_bp

            ON blood_pressures.patient_id = latest_bp.patient_id
                AND recorded_at = latest_bp.last_record

        INNER JOIN patients 
            ON blood_pressures.patient_id = patients.id;

{% endfor %}
"""

eot_query = """
{% for date in dates %}
    INSERT INTO encounters_over_time(patient_id, 
                                     calendar_month,
                                     months_since_registration,
                                     months_since_encounter)

    SELECT 
        encounters.patient_id, 

        {{date}} 
            as calendar_month, 

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', patients.recorded_at)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', patients.recorded_at)) 
            as months_since_registration,

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', encounters.encountered_on)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', encounters.encountered_on)) 
            as months_since_encounter


        FROM encounters

        INNER JOIN
        (
            SELECT patient_id, max(encountered_on) as last_record
            FROM encounters
            WHERE encountered_on::date <= {{date}}::date
            GROUP BY patient_id
        ) as latest_encounter

            ON encounters.patient_id = latest_encounter.patient_id
                AND encounters.encountered_on = latest_encounter.last_record

        INNER JOIN patients 
            ON encounters.patient_id = patients.id;

{% endfor %}
"""

psot_query = """
{% for date in dates %}
    INSERT INTO patient_states_over_time(patient_id, 
                                            months_since_registration,
                                            calendar_month,
                                            diagnosed_disease_state,
                                            treatment_state,
                                            bp_observation_state)
    SELECT
        patients.id as patient_id,

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', patients.recorded_at)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', patients.recorded_at)) 
            as months_since_registration,

        {{date}} 
            as calendar_month, 


        CASE 
            WHEN medical_histories.hypertension = 'yes' AND (bpoot.systolic >= 180 OR bpoot.diastolic >= 110) THEN 'Stage 3'
            WHEN medical_histories.hypertension = 'yes' AND (bpoot.systolic >= 160 OR bpoot.diastolic >= 100) THEN 'Stage 2'
            WHEN medical_histories.hypertension = 'yes' AND (bpoot.systolic >= 140 OR bpoot.diastolic >= 90) THEN 'Stage 1'
            WHEN medical_histories.hypertension = 'yes' AND (bpoot.systolic < 140 AND bpoot.diastolic < 90) THEN 'Controlled'
            WHEN medical_histories.hypertension = 'yes' AND (bpoot.systolic IS null) THEN 'Hypertensive Unknown Stage'
            WHEN medical_histories.hypertension = 'unknown' THEN 'Unknown'
            WHEN medical_histories.hypertension = 'no' THEN 'Not hypertensive'
            ELSE 'Undefined'
        END
            as diagnosed_disease_state,

        CASE
            WHEN patients.status = 'dead' THEN 'Not needed'
            WHEN patients.status = 'migrated' THEN 'Not needed'
            WHEN medical_histories.hypertension = 'no' THEN 'Not needed'
            WHEN eot.months_since_encounter < 3 THEN 'Less than 3 months'
            WHEN eot.months_since_encounter < 6 THEN 'Between 3 and 6 months'
            WHEN eot.months_since_encounter < 9 THEN 'Between 6 and 9 months'
            WHEN eot.months_since_encounter < 12 THEN 'Between 9 and 12 months'
            WHEN eot.months_since_encounter > 12 THEN 'More than 12 months'
            WHEN eot.months_since_encounter IS null THEN 'No encounter'
            ELSE 'Undefined'
        END
            as treatment_state,

        CASE
            WHEN bpoot.months_since_bp_observation < 3 THEN 'Less than 3 months'
            WHEN bpoot.months_since_bp_observation < 6 THEN 'Between 3 and 6 months'
            WHEN bpoot.months_since_bp_observation < 9 THEN 'Between 6 and 9 months'
            WHEN bpoot.months_since_bp_observation < 12 THEN 'Between 9 and 12 months'
            WHEN bpoot.months_since_bp_observation > 12 THEN 'More than 12 months'
            WHEN bpoot.months_since_bp_observation IS null THEN 'No measurement'
            ELSE 'Undefined'
        END
            as bp_observation_state


        FROM patients

        INNER JOIN medical_histories ON patients.id = medical_histories.patient_id


        LEFT JOIN blood_pressure_observations_over_time as bpoot

        ON patients.id = bpoot.patient_id
            AND bpoot.calendar_month = {{date}}

        LEFT JOIN encounters_over_time as eot

        ON patients.id = eot.patient_id
            AND eot.calendar_month = {{date}}

    WHERE patients.recorded_at::date <= {{date}}::date;
{% endfor %}
"""

mot_query = """
{% for date in dates %}
    INSERT INTO medicine_over_time(patient_id, 
                                    calendar_month,
                                    months_since_registration,
                                    amlodipine,
                                    telmisartan,
                                    losartan,
                                    atenolol,
                                    enalapril,
                                    chlorthalidone,
                                    hydrochlorothiazide,
                                    other_bp_medications)

    SELECT
        patients.id,

        {{date}}
            AS calendar_month, 

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', patients.recorded_at)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', patients.recorded_at)) 
            AS months_since_registration,

        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                FILTER (WHERE clean_medicine_to_dosage.medicine = 'Amlodipine'),
            0)
            as amlodipine,
        
        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                FILTER (WHERE clean_medicine_to_dosage.medicine = 'Telmisartan'),
            0)
            as telmisartan,
        
        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                FILTER (WHERE clean_medicine_to_dosage.medicine = 'Losartan'),
            0)
            as losartan,
        
        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                FILTER (WHERE clean_medicine_to_dosage.medicine = 'Atenolol'),
            0)
            as atenolol,
        
        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                FILTER (WHERE clean_medicine_to_dosage.medicine = 'Enalapril'),
            0)
            as enalapril,
        
        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                FILTER (WHERE clean_medicine_to_dosage.medicine = 'Chlorthalidone'),
            0)
            as chlorthalidone,
        
        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                FILTER (WHERE clean_medicine_to_dosage.medicine = 'Hydrochlorothiazide'),
            0)
            as hydrochlorothiazide,
        
        COALESCE(
            SUM (clean_medicine_to_dosage.dosage)
                    FILTER (WHERE clean_medicine_to_dosage.medicine <> 'Amlodipine'
                                AND clean_medicine_to_dosage.medicine <> 'Telmisartan'
                                AND clean_medicine_to_dosage.medicine <> 'Losartan'
                                AND clean_medicine_to_dosage.medicine <> 'Atenolol'
                                AND clean_medicine_to_dosage.medicine <> 'Enalapril'
                                AND clean_medicine_to_dosage.medicine <> 'Chlorthalidone'
                                AND clean_medicine_to_dosage.medicine <> 'Hydrochlorothiazide'
                                AND medicine_purpose.hypertension = true),
            0)
            
            as other_bp_medications
        
        FROM patients
        
        LEFT JOIN (
            SELECT * 
                FROM prescription_drugs 
                
                WHERE prescription_drugs.created_at::date <= {{date}}::date
                    AND (prescription_drugs.is_deleted = false
                        OR (prescription_drugs.is_deleted = true
                            AND prescription_drugs.device_updated_at::date > {{date}}::date))
                   
            ) prescription_drugs
            ON patients.id = prescription_drugs.patient_id
        
        LEFT JOIN raw_to_clean_medicine
            --ON prescription_drugs.name = raw_to_clean_medicine.raw_name
            --    AND prescription_drugs.dosage = raw_to_clean_medicine.raw_dosage
            ON UPPER(REGEXP_REPLACE(prescription_drugs.name, '\s+', '','g')) = UPPER(REGEXP_REPLACE(raw_to_clean_medicine.raw_name, '\s+', '','g'))
                AND UPPER(REGEXP_REPLACE(prescription_drugs.dosage, '\s+', '','g')) = UPPER(REGEXP_REPLACE(raw_to_clean_medicine.raw_dosage, '\s+', '','g'))
        LEFT JOIN clean_medicine_to_dosage
            ON raw_to_clean_medicine.rxcui = clean_medicine_to_dosage.rxcui
        
        LEFT JOIN medicine_purpose
            ON clean_medicine_to_dosage.medicine = medicine_purpose.name
            
        WHERE patients.recorded_at::date <= {{date}}::date
            
        GROUP BY patients.id, patients.recorded_at;

{% endfor %}
"""

protocol_sot_query = """
{% for date in dates %}
    INSERT INTO protocol_steps_over_time(patient_id,
                                            protocol_id,
                                            calendar_month,
                                            months_since_registration,
                                            step)

    SELECT 
        medicine_over_time.patient_id
            AS patient_id,

        facility_groups.protocol_id
            AS protocol_id,

        {{date}}
            AS calendar_month, 

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', patients.recorded_at)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', patients.recorded_at)) 
            AS months_since_registration,

        protocol_step_definition.step
            AS step

        FROM 
            medicine_over_time

        INNER JOIN patients
            ON medicine_over_time.patient_id = patients.id

        LEFT JOIN facilities
            ON patients.assigned_facility_id = facilities.id

        LEFT JOIN facility_groups
            ON facilities.facility_group_id = facility_groups.id

        LEFT JOIN protocol_step_definition
            ON facility_groups.protocol_id = protocol_step_definition.protocol_id
                AND medicine_over_time.amlodipine = protocol_step_definition.amlodipine
                AND medicine_over_time.telmisartan = protocol_step_definition.telmisartan
                AND medicine_over_time.losartan = protocol_step_definition.losartan
                AND medicine_over_time.atenolol = protocol_step_definition.atenolol
                AND medicine_over_time.enalapril = protocol_step_definition.enalapril
                AND medicine_over_time.chlorthalidone = protocol_step_definition.chlorthalidone
                AND medicine_over_time.hydrochlorothiazide = protocol_step_definition.hydrochlorothiazide
                AND medicine_over_time.other_bp_medications = protocol_step_definition.other_bp_medications

        WHERE 
            medicine_over_time.calendar_month = {{date}};

{% endfor %}
"""

vcot_query = """
{% for date in dates %}
    INSERT INTO visit_counts_over_time(patient_id,
                                        calendar_month,
                                        months_since_registration,
                                        encounters,
                                        bp_observations)

    SELECT
        patients.id
            AS patient_id,

        {{date}} 
            AS calendar_month, 

        (DATE_PART('year', {{date}}::date) - DATE_PART('year', patients.recorded_at)) * 12 +
        (DATE_PART('month', {{date}}::date) - DATE_PART('month', patients.recorded_at)) 
            AS months_since_registration,

        COUNT(DISTINCT encounters.id)
            FILTER (WHERE encounters.encountered_on <= {{date}})

            AS encounters,

        COUNT(DISTINCT blood_pressures.id)
            FILTER (WHERE blood_pressures.recorded_at::date <= {{date}})

            AS bp_observations


        FROM patients

        LEFT JOIN encounters
            ON patients.id = encounters.patient_id

        LEFT JOIN blood_pressures
            ON patients.id = blood_pressures.patient_id

        WHERE patients.recorded_at::date <= {{date}}

        GROUP BY patients.id;

{% endfor %}
"""


def generate_query(query):
    template = Template(query)
    print(template.render(dates=dates))


generate_query(bpoot_query)
generate_query(eot_query)
generate_query(psot_query)
generate_query(mot_query)
generate_query(protocol_sot_query)
generate_query(vcot_query)