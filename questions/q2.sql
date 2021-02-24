--Question 2: Cross-sectional hypertension control

SELECT 
	COUNT (DISTINCT psot.patient_id) 
		FILTER (WHERE psot.diagnosed_disease_state = 'Controlled'
            		AND (psot.bp_observation_state = 'Less than 3 months'
            			OR psot.bp_observation_state = 'Between 3 and 6 months'
                		OR psot.bp_observation_state = 'Between 6 and 9 months'
                		OR psot.bp_observation_state = 'Between 9 and 12 months')
		as numerator,
					
	COUNT(DISTINCT psot.patient_id)
		as denominator
	
	FROM patient_states_over_time as psot
	
	INNER JOIN patients 
		ON psot.patient_id = patients.id

	INNER JOIN medical_histories 
		ON psot.patient_id = medical_histories.patient_id
	
	--Look at hypertensive patients, registered at least 3 months ago, as of a certain date
	WHERE psot.calendar_month = '2021/01/31' 
		AND psot.months_since_registration >= 3
		AND medical_histories.hypertension = 'yes'
		--Do not include patients "lost to follow up" (as of the given date) or are dead or deleted.   		
		AND psot.bp_observation_state <> 'More than 12 months' 
		AND psot.bp_observation_state <> 'No measurement' -- Should these be excluded?
		AND patient.status <> 'dead' --Note: We do not exclude migrated, unresponsive, inactive
		AND patients.deleted_at = NULL