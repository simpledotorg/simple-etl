--question 6

SELECT 

	COUNT (DISTINCT psot.patient_id) 
		FILTER (WHERE psot.bp_observation_state = 'Less than 3 months')
				--OR psot.bp_observation_state = 'Between 3 and 6 months')
			
		as numerator,
					
	COUNT(DISTINCT psot.patient_id)
		as denominator
	
	FROM patient_states_over_time as psot
	
	INNER JOIN patients 
		ON psot.patient_id = patients.id
		
	--INNER JOIN visit_count_over_time
	--	ON psot.patient_id = visit_count_over_time.patient_id
	--		AND psot.months_since_registration = visit_count_over_time.months_since_registration
	
	WHERE psot.calendar_mont = '2021/01/31'
		AND psot.months_since_registration = 6
		--Do not include patients dead or deleted. (Lost to follow up are excluded above)
		AND patient.status <> 'dead' --Note: We do not exclude migrated, unresponsive, inactive
		AND patients.deleted_at = NULL