--Question 3: Treatment inertia
--What percent of individuals with uncontrolled hypertension have their regimens escalated?

SELECT 
	COUNT (DISTINCT psot.patient_id) 
		FILTER (--Patients who have uncontrolled hypertensions
			WHERE (psot.diagnosed_disease_state = 'Stage 1'
				OR psot.diagnosed_disese_state = 'Stage 2'
				OR psot.diagnosed_disese_state = 'Stage 3')
			--And ANY of the specified hypertension medications have been increased
			AND (current_meds.amlodipine > past_meds.amlodipine
				OR current_meds.telmisartan > past_meds.telmisartan
				OR current_meds.losartan > past_meds.losartan
				OR current_meds.atenolol > past_meds.atenolol
				OR current_meds.enalapril > past_meds.enalapril
				OR current_meds.chlorthalidone > past_meds.chlorthalidone)
				--Note: Patients who only have "current_meds.other_bp_medication" increaesd will not be included
		as numerator,
					
	COUNT(DISTINCT psot.patient_id)
		as denominator
	
	FROM patient_states_over_time as psot
	
	INNER JOIN patients 
		ON psot.patient_id = patients.id

	INNER JOIN medical_histories 
		ON psot.patient_id = medical_histories.patient_id
	
	INNER JOIN medicine_over_time current_meds
		ON psot.patient_id = current_meds.patient_id
			AND psot.months_since_registration = current_meds.months_since_registration
			
	INNER JOIN medicine_over_time past_meds
		ON psot.patient_id = past_meds.patient_id
			AND psot.months_since_registration = (past_meds.months_since_registration + 3)
	
	--Look at hypertensive patients, registered at least 3 months ago, as of a certain date, who have a recent BP observations
	WHERE psot.calendar_month = '2021/01/31'
		AND psot.months_since_registration >= 3
		AND medical_histories.hypertension = 'yes'
		AND psot.bp_observation_state = 'Less than 3 months'
		--Do not include patients dead or deleted. (Lost to follow up are excluded above)
		AND patient.status <> 'dead' --Note: We do not exclude migrated, unresponsive, inactive
		AND patients.deleted_at = NULL