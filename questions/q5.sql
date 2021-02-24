--question 5

SELECT 

	protocol_steps_over_time.protocol_id
		as protocol_id,
	
	protocol_steps_over_time.step
		as step,
		
	psot.diagnosed_disease_state
		as diagnosed_disease_state,

	COUNT (DISTINCT psot.patient_id) 
		FILTER (WHERE psot.diagnosed_disease_state = 'Controlled'
            			AND psot.bp_observation_state = 'Less than 3 months')
			
		as numerator,
					
	COUNT(DISTINCT psot.patient_id)
		as denominator
	
	FROM patient_states_over_time as psot
	
	INNER JOIN patients 
		ON psot.patient_id = patients.id

	INNER JOIN medical_histories 
		ON psot.patient_id = medical_histories.patient_id
	
	INNER JOIN protocol_steps_over_time
		ON psot.patient_id = protocol_steps_over_time.patient_id
			AND psot.months_since_registration = protocol_steps_over_time.months_since_registration
	
	--Look at hypertensive patients, as of a certain date, who have a BP observation within the last year
	WHERE psot.calendar_month = '2021/01/31' 
		AND medical_histories.hypertension = 'yes'
		AND (psot.bp_observation_state = 'Less than 3 months'
            		OR psot.bp_observation_state = 'Between 3 and 6 months'
                	OR psot.bp_observation_state = 'Between 6 and 9 months'
                	OR psot.bp_observation_state = 'Between 9 and 12 months')
		--Do not include patients who are recently registered, dead, or deleted. (Lost to follow up are excluded above)
		AND psot.months_since_registration >= 3
		AND patient.status <> 'dead' --Note: We do not exclude migrated, unresponsive, inactive
		AND patients.deleted_at = NULL
		
	GROUP BY protocol_steps_over_time.protocol_id, protocol_steps_over_time.step, psot.diagnosed_disease_state