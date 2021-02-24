--Question 1: Cohort Hypertension Control

SELECT 
	COUNT (DISTINCT psot.patient_id) 
		FILTER (WHERE psot.bp_observation_state = 'Less than 3 months' 
				AND psot.diagnosed_disease_state = 'Controlled')
		as numerator,
					
	COUNT(DISTINCT psot.patient_id)
		as denominator
	
	FROM patient_states_over_time as psot
	
	INNER JOIN patients 
		ON psot.patient_id = patients.id

	INNER JOIN medical_histories 
		ON psot.patient_id = medical_histories.patient_id
	
	--Look at hypertensive patients, registered 3 to 6 months ago*, as of a certain date
	WHERE psot.calendar_month = '2020/06/30' 
		AND psot.months_since_registration >= 3 --AND patients.recorded_at::date <= '2020/03/31'
		AND psot.months_since_registration < 6 --AND patients.recorded_at::date >= '2020/01/01'
		AND medical_histories.hypertension = 'yes'
		--Do not include patients "lost to follow up" (as of the given date) or are dead or deleted.   		
		AND psot.bp_observation_state <> 'More than 12 months' 
		AND psot.bp_observation_state <> 'No measurement' -- Should these be excluded as well?
		AND patient.status <> 'dead' --Note: We do not exclude a status of migrated, unresponsive, or inactive
		AND patients.deleted_at = NULL
		