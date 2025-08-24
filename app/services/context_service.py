def determine_metabolic_phase(meal_timing):
    """Determine metabolic phase based on meal timing"""
    if not meal_timing:
        return {
            "phase": "Unknown",
            "expected_pattern": "Unpredictable",
            "is_critical_window": False,
            "special_notes": "insufficient meal timing data"
        }
    
    phases = {
        "Currently eating/just finished (0-30 min)": {
            "phase": "Early Postprandial",
            "expected_pattern": "Initial glucose rise",
            "is_critical_window": False,
            "special_notes": "early insulin response phase, voice may show stress markers"
        },
        "30 minutes to 1 hour ago": {
            "phase": "Early Postprandial",
            "expected_pattern": "Glucose rising",
            "is_critical_window": False,
            "special_notes": "early postprandial phase, glucose beginning to rise"
        },
        "1-2 hours ago": {
            "phase": "Peak Postprandial",
            "expected_pattern": "Glucose at or near peak",
            "is_critical_window": True,
            "special_notes": "peak postprandial glucose phase (most critical for detection)"
        },
        "2-4 hours ago": {
            "phase": "Late Postprandial",
            "expected_pattern": "Glucose normalizing",
            "is_critical_window": False,
            "special_notes": "late postprandial, glucose normalizing in healthy individuals"
        },
        "4-8 hours ago": {
            "phase": "Post-absorptive",
            "expected_pattern": "Return to baseline",
            "is_critical_window": False,
            "special_notes": "return to baseline, fasting-like state"
        },
        "8+ hours/overnight fasting": {
            "phase": "Fasting",
            "expected_pattern": "Baseline glucose levels",
            "is_critical_window": False,
            "special_notes": "true fasting state, baseline glucose patterns"
        },
        "I don't remember": {
            "phase": "Unknown",
            "expected_pattern": "Unpredictable",
            "is_critical_window": False,
            "special_notes": "uncertainty flag, reduced confidence in predictions"
        }
    }
    
    return phases.get(meal_timing, {
        "phase": "Unknown",
        "expected_pattern": "Unpredictable",
        "is_critical_window": False,
        "special_notes": "unrecognized meal timing pattern"
    })

def analyze_symptom_constellation(symptoms):
    """Analyze symptom constellation for glucose direction"""
    if not symptoms or len(symptoms) == 0:
        return {
            "cluster_type": "Asymptomatic",
            "direction": "Neutral",
            "urgency": "Low"
        }
    
    # Define symptom groups
    hyperglycemia_symptoms = [
        "Unusual thirst or dry mouth",
        "Frequent urination",
        "Blurred vision"
    ]
    
    hypoglycemia_symptoms = [
        "Shakiness or tremors",
        "Confusion or difficulty concentrating"
    ]
    
    nonspecific_symptoms = [
        "Fatigue or drowsiness",
        "Nausea or vomiting"
    ]
    
    # Count symptoms in each category
    hyper_count = sum(1 for s in symptoms if s in hyperglycemia_symptoms)
    hypo_count = sum(1 for s in symptoms if s in hypoglycemia_symptoms)
    nonspecific_count = sum(1 for s in symptoms if s in nonspecific_symptoms)
    
    # Determine direction
    if hyper_count > hypo_count:
        direction = "Hyperglycemic"
        cluster_type = "Hyperglycemia Cluster"
    elif hypo_count > hyper_count:
        direction = "Hypoglycemic"
        cluster_type = "Hypoglycemia Cluster"
    else:
        direction = "Mixed"
        cluster_type = "Mixed Symptom Cluster"
    
    # Determine urgency
    total_symptoms = len(symptoms)
    if total_symptoms >= 3:
        urgency = "High"
    elif total_symptoms == 2:
        urgency = "Moderate"
    else:
        urgency = "Low"
    
    # Increase urgency for specific concerning symptoms
    if "Confusion or difficulty concentrating" in symptoms:
        urgency = "High"
    
    return {
        "cluster_type": cluster_type,
        "direction": direction,
        "urgency": urgency
    }

def get_special_considerations(diabetes_status):
    """Get special considerations based on diabetes status"""
    considerations = {
        "No diabetes, no family history": "minimal baseline risk with focus on acute glucose spikes",
        "No diabetes, family history of diabetes": "enhanced sensitivity for prediabetic patterns",
        "Prediabetes/borderline diabetes": "monitoring for progression indicators",
        "Type 1 diabetes": "high variability with focus on rapid changes and ketone-related voice markers",
        "Type 2 diabetes, well-controlled": "moderate stability with attention to medication compliance indicators",
        "Type 2 diabetes, poorly controlled": "high baseline risk with multiple complication indicators",
        "Gestational diabetes": "pregnancy-specific voice changes with hormonal considerations",
        "Unknown": "general glucose assessment without specific risk stratification"
    }
    
    return considerations.get(diabetes_status, "general glucose assessment without specific risk stratification")

def calculate_risk_level(diabetes_status):
    """Calculate baseline risk level based on diabetes status"""
    risk_levels = {
        "No diabetes, no family history": 0.1,
        "No diabetes, family history of diabetes": 0.3,
        "Prediabetes/borderline diabetes": 0.5,
        "Type 1 diabetes": 0.7,
        "Type 2 diabetes, well-controlled": 0.5,
        "Type 2 diabetes, poorly controlled": 0.8,
        "Gestational diabetes": 0.6
    }
    
    return risk_levels.get(diabetes_status, 0.4)

def get_variability_profile(diabetes_status):
    """Get expected glucose variability profile based on diabetes status"""
    profiles = {
        "No diabetes, no family history": "Low variability, stable patterns",
        "No diabetes, family history of diabetes": "Low-moderate variability, possible postprandial spikes",
        "Prediabetes/borderline diabetes": "Moderate variability, elevated postprandial response",
        "Type 1 diabetes": "High variability, rapid fluctuations possible",
        "Type 2 diabetes, well-controlled": "Moderate variability, managed fluctuations",
        "Type 2 diabetes, poorly controlled": "High variability, unpredictable patterns",
        "Gestational diabetes": "Moderate-high variability, hormone-influenced patterns"
    }
    
    return profiles.get(diabetes_status, "Unknown variability profile")
