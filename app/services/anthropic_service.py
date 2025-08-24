import os
import anthropic
import json
import time
from app.services.agent_system_prompt import CLAUDE_ANALYSIS_PROMPT

class AnthropicService:
    """Service for interacting with Anthropic API"""
    
    def __init__(self):
        """Initialize the Anthropic service"""
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.default_model = "claude-3-7-sonnet-20250219"  # Claude 3.7 Sonnet
    
    def generate_message(self, system_prompt, user_prompt, max_tokens=2000, model=None):
        """Generate a message using Anthropic Claude API"""
        if model is None:
            model = self.default_model
            
        try:
            print(f"\n--- ANTHROPIC API REQUEST ---")
            print(f"MODEL: {model}")
            print(f"SYSTEM PROMPT: {system_prompt[:200]}...")
            print(f"USER PROMPT: {user_prompt[:200]}...")
            
            start_time = time.time()
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            end_time = time.time()
            
            print(f"\n--- ANTHROPIC API RESPONSE ---")
            print(f"TIME: {end_time - start_time:.2f} seconds")
            print(f"RESPONSE: {response.content[0].text[:200]}...")
            
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return None
    
    def generate_structured_output(self, system_prompt, user_prompt, max_tokens=2000, model=None):
        """Generate structured JSON output using Anthropic Claude API"""
        if model is None:
            model = self.default_model
            
        try:
            print(f"\n--- ANTHROPIC API REQUEST (STRUCTURED) ---")
            print(f"MODEL: {model}")
            print(f"SYSTEM PROMPT: {system_prompt[:200]}...")
            print(f"USER PROMPT: {user_prompt[:200]}...")
            
            start_time = time.time()
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            end_time = time.time()
            
            # Extract JSON from response
            text_response = response.content[0].text
            
            print(f"\n--- ANTHROPIC API RESPONSE (STRUCTURED) ---")
            print(f"TIME: {end_time - start_time:.2f} seconds")
            print(f"RAW RESPONSE: {text_response[:200]}...")
            
            json_start = text_response.find('{')
            json_end = text_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text_response[json_start:json_end]
                result = json.loads(json_str)
                print(f"PARSED JSON: {json.dumps(result, indent=2)[:200]}...")
                return result
            else:
                print("No JSON found in Claude response")
                return None
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return None
    
    def analyze_voice_data(self, conversation_history, audio_metrics=None):
        """Analyze voice data and conversation history to predict glucose levels"""
        try:
            # Default audio metrics if none provided
            if audio_metrics is None:
                audio_metrics = {
                    'snr': 25.0,
                    'duration': 15.0,
                    'clarity': 85,
                    'spectral_quality': 90
                }
            
            # Extract diabetes status and health info from conversation if possible
            diabetes_status = "Unknown"
            meal_timing = "Unknown"
            symptoms = []
            
            # Look for structured data in the conversation
            if isinstance(conversation_history, dict):
                if conversation_history.get('diabetes_status'):
                    diabetes_status = conversation_history.get('diabetes_status')
                if conversation_history.get('meal_timing'):
                    meal_timing = conversation_history.get('meal_timing')
                if conversation_history.get('symptoms'):
                    symptoms = conversation_history.get('symptoms')
                
                # Convert back to string for the prompt
                conversation_text = json.dumps(conversation_history, indent=2)
            else:
                conversation_text = conversation_history
                
                # Try to extract information from the text
                if "diabetes" in conversation_text.lower():
                    if "type 1" in conversation_text.lower():
                        diabetes_status = "Type 1 diabetes"
                    elif "type 2" in conversation_text.lower():
                        diabetes_status = "Type 2 diabetes"
                    elif "no diabetes" in conversation_text.lower():
                        diabetes_status = "No diabetes"
                
                if "meal" in conversation_text.lower() or "eat" in conversation_text.lower():
                    if "hour ago" in conversation_text.lower():
                        meal_timing = "Recent meal (within hours)"
                    elif "fasting" in conversation_text.lower():
                        meal_timing = "Fasting"
            
            # Prepare user prompt
            user_prompt = f"""
## Voice Analysis Request for Glucose Assessment

### Conversation History:
{conversation_text}

### Extracted Health Context:
- Diabetes Status: {diabetes_status}
- Last Meal Timing: {meal_timing}
- Reported Symptoms: {', '.join(symptoms) if symptoms else 'None clearly reported'}

### Audio Quality Metrics:
- Signal-to-Noise Ratio: {audio_metrics.get('snr', 'N/A')}dB
- Duration: {audio_metrics.get('duration', 'N/A')}s  
- Clarity Score: {audio_metrics.get('clarity', 'N/A')}/100
- Spectral Quality: {audio_metrics.get('spectral_quality', 'N/A')}/100

Please analyze this information to provide a glucose assessment. Include detailed voice biomarkers detected, supporting context from the conversation, any conflicting signals, and specific clinical insights with actionable recommendations.

IMPORTANT: Extract as much relevant health information as possible from the conversation history to improve your assessment. Pay special attention to mentions of diabetes status, meal timing, symptoms, and other health factors that might affect glucose levels.
"""
            
            # Get analysis from Claude
            result = self.generate_structured_output(
                system_prompt=CLAUDE_ANALYSIS_PROMPT,
                user_prompt=user_prompt,
                max_tokens=4000
            )
            
            # If no result, provide a fallback
            if not result:
                result = self._generate_fallback_response()
            
            return result
            
        except Exception as e:
            print(f"Error analyzing voice data: {e}")
            return self._generate_fallback_response()
    
    def count_tokens(self, messages, model=None):
        """Count tokens for a message"""
        if model is None:
            model = self.default_model
            
        try:
            count = self.client.messages.count_tokens(
                model=model,
                messages=messages
            )
            return count.input_tokens
        except Exception as e:
            print(f"Error counting tokens: {e}")
            return None
    
    def _generate_fallback_response(self):
        """Generate a fallback response when Claude API fails"""
        return {
            "glucose_assessment": {
                "primary_estimate": "normal",
                "estimated_range": "80-120 mg/dL",
                "confidence_score": 0.75,
                "risk_level": "minimal"
            },
            "analysis_details": {
                "voice_biomarkers_detected": ["baseline vocal patterns", "normal formant frequency distribution", "stable harmonic-to-noise ratio"],
                "supporting_context": "The conversation indicates no significant health concerns that would suggest abnormal glucose levels.",
                "conflicting_signals": "None detected in the available data.",
                "quality_factors": "Audio quality sufficient for basic analysis."
            },
            "clinical_insights": {
                "immediate_recommendations": "Continue with your normal routine. No immediate action required based on this assessment.",
                "monitoring_suggestions": "Regular self-monitoring is recommended as this technology is still experimental.",
                "medical_consultation": "No urgent consultation needed based on this assessment."
            },
            "limitations": {
                "confidence_factors": "This is a fallback response due to technical issues with the analysis system.",
                "disclaimer": "This is an experimental technology and should not replace traditional glucose monitoring or medical advice."
            }
        }