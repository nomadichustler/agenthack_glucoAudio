import os
import json
import anthropic
from app.services.context_service import determine_metabolic_phase, analyze_symptom_constellation, get_special_considerations
from app.services.anthropic_service import AnthropicService

class ClaudeInferenceAgent:
    """Agent for glucose level prediction with contextual reasoning using Claude API"""
    
    def __init__(self):
        try:
            self.anthropic_service = AnthropicService()
            self.client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        except Exception as e:
            print(f"Error initializing Claude inference agent: {e}")
    
    async def analyze_glucose(self, embeddings, user_context, audio_quality):
        """Analyze voice embeddings and context to predict glucose levels"""
        if not embeddings or not user_context:
            return {
                "error": "Missing embeddings or user context",
                "glucose_prediction": self._generate_fallback_response()
            }
        
        prompt = self.build_analysis_prompt(embeddings, user_context, audio_quality)
        claude_response = await self.call_claude(prompt)
        glucose_prediction = await self.parse_response(claude_response)
        
        return {
            "glucose_prediction": glucose_prediction,
            "raw_claude_response": claude_response
        }
    
    def build_analysis_prompt(self, voice_embedding, user_responses, audio_metrics):
        """Build a structured prompt for Claude based on user context"""
        system_prompt = """
You are GlucoVoice-AI, a specialized biomarker analysis system for non-invasive glucose estimation through voice pattern recognition. You operate as part of a multi-agent system coordinated by Portia AI SDK.

## Core Competencies:
1. Voice embedding pattern recognition for metabolic indicators
2. Bayesian inference combining voice data with physiological context
3. Risk stratification based on diabetes phenotypes
4. Confidence calibration for healthcare applications

## Input Data Structure:
- voice_embedding: 512-dimensional wav2vec2.0 feature vector
- user_context: {diabetes_status, meal_timing, symptoms, demographics}
- audio_metrics: {snr, duration, clarity, spectral_quality}
- conversation_history: Transcript of the health questionnaire conversation
- temporal_data: {time_of_day, recording_environment}

## Analysis Framework:

### Phase 1: Embedding Pattern Analysis
- Identify spectral anomalies in voice embedding clusters
- Map to known glucose-voice biomarker correlations:
  * Fundamental frequency variations (F0 instability) → glucose volatility
  * Harmonic-to-noise ratio changes → dehydration/hyperglycemia
  * Formant frequency shifts → vocal tract tension changes
  * Prosodic pattern alterations → neurological glucose effects

### Phase 2: Contextual Bayesian Integration
Apply user context as prior probabilities:
- No diabetes: P(normal glucose) = 0.85, P(elevated) = 0.12, P(low) = 0.03
- Type 1 diabetes: P(normal) = 0.45, P(elevated) = 0.35, P(low) = 0.20
- Type 2 well-controlled: P(normal) = 0.70, P(elevated) = 0.25, P(low) = 0.05
- Type 2 poorly-controlled: P(normal) = 0.40, P(elevated) = 0.55, P(low) = 0.05

Adjust based on meal timing:
- Fasting state: Reduce P(elevated) by 0.2, increase P(normal) by 0.15
- 1-2hr post-meal: Increase P(elevated) by 0.3 for non-diabetics, 0.5 for diabetics

### Phase 3: Symptom Integration
Weight symptoms as likelihood multipliers:
- Thirst/polyuria: 3x likelihood of hyperglycemia
- Shakiness: 5x likelihood of hypoglycemia  
- Fatigue: 2x likelihood of glucose dysregulation
- Multiple symptoms: Exponential confidence boost

### Phase 4: Confidence Calibration
Calculate confidence scores based on:
- Voice embedding cluster distance from training centroids
- Consistency of multiple biomarker signals
- Quality of audio input (SNR > 20dB = high confidence)
- Alignment between symptoms and voice patterns
- Completeness of questionnaire responses

## Output Requirements:
Generate structured JSON response:
{
  "glucose_assessment": {
    "primary_estimate": "normal/elevated/low/critical",
    "estimated_range": "mg/dL range if applicable",
    "confidence_score": 0.0-1.0,
    "risk_level": "minimal/low/moderate/high/critical"
  },
  "analysis_details": {
    "voice_biomarkers_detected": ["list of specific patterns"],
    "supporting_context": "how user data supports assessment",
    "conflicting_signals": "any contradictory indicators",
    "quality_factors": "audio and data quality assessment"
  },
  "clinical_insights": {
    "immediate_recommendations": "actionable steps",
    "monitoring_suggestions": "what to watch for",
    "medical_consultation": "when to seek professional care"
  },
  "limitations": {
    "confidence_factors": "what affects reliability",
    "disclaimer": "experimental nature, not diagnostic"
  }
}

## Critical Constraints:
- Never provide definitive medical diagnoses
- Always include confidence intervals and limitations
- Flag critical situations requiring immediate medical attention
- Maintain HIPAA-compliant language in all outputs
- Adjust language complexity based on user's health literacy level

## Research Integration:
Base analysis on established voice-glucose correlations from:
- Vocal jitter/shimmer variations in diabetic populations
- Spectral centroid shifts during glucose fluctuations  
- Pause patterns and speech rhythm changes
- Acoustic energy distribution modifications

Remember: You are providing supplementary health insights, not replacing traditional glucose monitoring or medical care.
"""
        
        # Extract conversation history from user_responses if available
        conversation_history = ""
        if user_responses.get('conversation'):
            conversation_history = user_responses.get('conversation')
        elif user_responses.get('user_context') and user_responses.get('user_context').get('conversation_history'):
            conversation_turns = user_responses.get('user_context').get('conversation_history', [])
            for turn in conversation_turns:
                role = turn.get('role', '')
                text = turn.get('text', '')
                conversation_history += f"{role.capitalize()}: {text}\n\n"
        
        # Get diabetes status and other health info from conversation or user_context
        diabetes_status = "Unknown"
        meal_timing = "Unknown"
        symptoms = []
        
        # Try to extract from user_context first
        if user_responses.get('user_context'):
            context = user_responses.get('user_context')
            if context.get('diabetes_status'):
                diabetes_status = context.get('diabetes_status')
            if context.get('meal_timing'):
                meal_timing = context.get('meal_timing')
            if context.get('symptoms'):
                symptoms = context.get('symptoms')
            
            # Also try to extract from responses object if present
            if context.get('responses'):
                responses = context.get('responses')
                if responses.get('diabetes_status'):
                    diabetes_status = responses.get('diabetes_status')
                if responses.get('meal_timing'):
                    meal_timing = responses.get('meal_timing')
                if responses.get('symptoms'):
                    symptoms = responses.get('symptoms')
        
        # Extract directly from user_responses if available
        if user_responses.get('diabetes_status'):
            diabetes_status = user_responses.get('diabetes_status')
        if user_responses.get('meal_timing'):
            meal_timing = user_responses.get('meal_timing')
        if user_responses.get('symptoms'):
            symptoms = user_responses.get('symptoms')
        
        embedding_preview = voice_embedding[:10]
        metabolic_phase = determine_metabolic_phase(meal_timing)
        
        user_prompt = f"""
## Voice Analysis Request for Glucose Assessment

### Voice Data:
Embedding Vector Preview (first 10 values): {embedding_preview}
Audio Quality Metrics:
- Signal-to-Noise Ratio: {audio_metrics.get('snr', 'N/A')}dB
- Duration: {audio_metrics.get('duration', 'N/A')}s  
- Clarity Score: {audio_metrics.get('clarity', 'N/A')}/100
- Spectral Completeness: {audio_metrics.get('spectral_quality', 'N/A')}%

### User Context Profile:
Diabetes Status: {diabetes_status}
Metabolic State: {metabolic_phase.get('phase', 'Unknown')} 
- Last Food Intake: {meal_timing}
- Expected Glucose Pattern: {metabolic_phase.get('expected_pattern', 'Unknown')}
- Critical Window: {metabolic_phase.get('is_critical_window', False)}
"""
        
        if symptoms:
            symptom_analysis = analyze_symptom_constellation(symptoms)
            user_prompt += f"""
Clinical Symptoms Present: {', '.join(symptoms)}
- Symptom Cluster Analysis: {symptom_analysis.get('cluster_type', 'Unknown')}
- Glucose Direction Indicator: {symptom_analysis.get('direction', 'Unknown')}
- Urgency Level: {symptom_analysis.get('urgency', 'Low')}
"""
        
        # Add conversation history if available
        if conversation_history:
            user_prompt += f"""
### Conversation History:
{conversation_history}
"""
        
        user_prompt += f"""
### Analysis Request:
Please perform comprehensive voice biomarker analysis for glucose estimation using the above context. Focus on:

1. **Pattern Recognition**: Identify specific voice embedding patterns consistent with glucose-related physiological changes
2. **Contextual Integration**: Weight voice signals against user's diabetes status and current metabolic state  
3. **Symptom Correlation**: Assess alignment between reported symptoms and voice biomarker patterns
4. **Conversation Analysis**: Extract relevant health information from the questionnaire conversation
5. **Confidence Calibration**: Provide realistic confidence intervals based on data quality and consistency

### Special Considerations:
- User's diabetes status suggests {get_special_considerations(diabetes_status)}
- Current metabolic timing indicates {metabolic_phase.get('special_notes', 'Unknown')}
- Audio quality {'supports high-confidence analysis' if audio_metrics.get('snr', 0) > 20 else 'requires cautious interpretation'}

Please provide detailed analysis with structured JSON output as specified in your system instructions.
"""
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    async def call_claude(self, prompt):
        """Call Claude API with the generated prompt"""
        try:
            return await self.anthropic_service.generate_message(
                system_prompt=prompt["system"],
                user_prompt=prompt["user"],
                max_tokens=2000,
                model="claude-3-7-sonnet-20250219"
            )
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return None
    
    async def parse_response(self, claude_response):
        """Parse and validate Claude's response"""
        if not claude_response:
            return self._generate_fallback_response()
        
        try:
            json_start = claude_response.find('{')
            json_end = claude_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = claude_response[json_start:json_end]
                parsed = json.loads(json_str)
                self._validate_response(parsed)
                return parsed
            else:
                return self._generate_fallback_response()
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            return self._generate_fallback_response()
    
    def _validate_response(self, response):
        """Validate that response has all required fields"""
        required_sections = ['glucose_assessment', 'analysis_details', 'clinical_insights', 'limitations']
        for section in required_sections:
            if section not in response:
                response[section] = {}
        
        if 'glucose_assessment' in response:
            if 'primary_estimate' not in response['glucose_assessment']:
                response['glucose_assessment']['primary_estimate'] = 'normal'
            if 'confidence_score' not in response['glucose_assessment']:
                response['glucose_assessment']['confidence_score'] = 0.5
    
    def _generate_fallback_response(self):
        """Generate a fallback response when Claude API fails"""
        return {
            "glucose_assessment": {
                "primary_estimate": "normal",
                "estimated_range": "80-120 mg/dL",
                "confidence_score": 0.3,
                "risk_level": "minimal"
            },
            "analysis_details": {
                "voice_biomarkers_detected": ["baseline vocal patterns"],
                "supporting_context": "Limited analysis due to API error",
                "conflicting_signals": "Unable to process voice data completely",
                "quality_factors": "Analysis compromised due to technical issues"
            },
            "clinical_insights": {
                "immediate_recommendations": "Please try again or use traditional glucose monitoring",
                "monitoring_suggestions": "Continue with your regular monitoring schedule",
                "medical_consultation": "Follow your healthcare provider's advice"
            },
            "limitations": {
                "confidence_factors": "Technical error in processing",
                "disclaimer": "This is an experimental technology and should not replace traditional glucose monitoring"
            }
        }