import os
import requests
import json
import tempfile
from datetime import datetime
from app.services.elevenlabs_service import ElevenLabsService

class VoiceSynthesisAgent:
    """Agent for generating personalized audio feedback using ElevenLabs API"""
    
    def __init__(self):
        try:
            self.elevenlabs_service = ElevenLabsService()
            self.api_key = os.environ.get('ELEVENLABS_API_KEY')
            self.api_url = "https://api.elevenlabs.io/v1"
            self.voice_ids = {
                "serious_medical_voice": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                "confident_assistant": "D38z5RcWu1voky8WS1ja",    # Adam voice
                "cautious_assistant": "pNInz6obpgDQGcFmaJgB"      # Bella voice
            }
        except Exception as e:
            print(f"Error initializing Voice Synthesis agent: {e}")
    
    async def synthesize_response(self, prediction, user_profile):
        """Generate voice response based on glucose prediction"""
        if not prediction or not prediction.get('glucose_prediction'):
            return {
                "error": "Missing glucose prediction",
                "voice_response": None,
                "voice_script": None
            }
        
        glucose_prediction = prediction.get('glucose_prediction')
        script, voice_config = self.create_voice_script(glucose_prediction, user_profile)
        audio_response = await self.synthesize_voice(script, voice_config)
        
        return {
            "voice_response": audio_response,
            "voice_script": script
        }
    
    def create_voice_script(self, claude_output, user_profile):
        """Create personalized voice script based on analysis results"""
        try:
            confidence = claude_output['glucose_assessment']['confidence_score']
            risk_level = claude_output['glucose_assessment']['risk_level']
            estimate = claude_output['glucose_assessment']['primary_estimate']
            
            if risk_level in ['high', 'critical']:
                voice_config = {
                    'voice_id': self.voice_ids['serious_medical_voice'],
                    'stability': 0.8,
                    'clarity': 0.9
                }
                script = f"""
                Attention: Your voice analysis indicates a potentially {risk_level} glucose situation. 
                The AI detected patterns suggesting {estimate} blood sugar with {confidence*100:.0f}% confidence.
                
                {claude_output['clinical_insights'].get('immediate_recommendations', 'Please monitor your glucose levels.')}
                
                Please test your blood sugar immediately and consider contacting your healthcare provider.
                Remember, this is experimental technology and should not replace proper glucose monitoring.
                """
            
            elif confidence > 0.7:
                voice_config = {
                    'voice_id': self.voice_ids['confident_assistant'],
                    'stability': 0.7,
                    'clarity': 0.8
                }
                script = f"""
                Based on your voice analysis, I'm detecting patterns suggesting {estimate} glucose levels 
                with {confidence*100:.0f}% confidence.
                
                {claude_output['clinical_insights'].get('immediate_recommendations', 'Continue monitoring your glucose levels.')}
                
                {claude_output['clinical_insights'].get('monitoring_suggestions', 'Pay attention to any changes in how you feel.')}
                
                This analysis is experimental and should supplement, not replace, regular glucose monitoring.
                """
            
            else:  # Low confidence
                voice_config = {
                    'voice_id': self.voice_ids['cautious_assistant'],
                    'stability': 0.6,
                    'clarity': 0.7
                }
                script = f"""
                I've analyzed your voice sample, but I have limited confidence in this assessment. 
                The patterns suggest {estimate} glucose, but with only {confidence*100:.0f}% certainty.
                
                {claude_output['limitations'].get('confidence_factors', 'Several factors affected the analysis quality.')}
                
                For more reliable monitoring, please use traditional glucose testing methods.
                This experimental tool works best with clear audio and consistent conditions.
                """
            
            return script.strip(), voice_config
        
        except Exception as e:
            print(f"Error creating voice script: {e}")
            # Fallback script
            return "I'm sorry, but I couldn't generate a complete analysis of your voice sample. Please try again or use traditional glucose monitoring methods.", {
                'voice_id': self.voice_ids['cautious_assistant'],
                'stability': 0.6,
                'clarity': 0.7
            }
    
    async def synthesize_voice(self, script, voice_config):
        """Synthesize voice using ElevenLabs API"""
        try:
            # Use the ElevenLabs service to generate speech
            audio_data = self.elevenlabs_service.text_to_speech(
                text=script,
                voice_id=voice_config['voice_id'],
                stability=voice_config.get('stability', 0.7),
                similarity_boost=voice_config.get('clarity', 0.7),
                output_format="mp3_44100_128"
            )
            
            # In a real application, we would save this to storage and return the URL
            # For now, we'll just return a placeholder URL
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"https://storage.example.com/voice_responses/{timestamp}.mp3"
        except Exception as e:
            print(f"Error synthesizing voice: {e}")
            return None