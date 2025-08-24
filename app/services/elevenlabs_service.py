import os
import requests
import tempfile
import json
import time
from datetime import datetime

class ElevenLabsService:
    """Service for interacting with ElevenLabs API"""
    
    def __init__(self):
        """Initialize the ElevenLabs service"""
        self.api_key = os.environ.get('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable must be set")
        
        self.api_url = "https://api.elevenlabs.io/v1"
        self.voice_ids = {
            "serious_medical_voice": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            "confident_assistant": "D38z5RcWu1voky8WS1ja",    # Adam voice
            "cautious_assistant": "pNInz6obpgDQGcFmaJgB"      # Bella voice
        }
        
        # Voice agent ID
        self.agent_id = "agent_6901k3drb5ajej4b4qpc9aewej7w"
    
    def text_to_speech(self, text, voice_id="21m00Tcm4TlvDq8ikWAM", stability=0.7, similarity_boost=0.7, output_format="mp3_44100_128"):
        """Convert text to speech using ElevenLabs API"""
        try:
            # Prepare request
            url = f"{self.api_url}/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                },
                "output_format": output_format
            }
            
            # Make API call
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                # Save audio to temporary file
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"voice_response_{timestamp}.mp3"
                
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_path = temp_file.name
                    temp_file.write(response.content)
                
                return temp_path
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Error synthesizing voice: {e}")
            return None
    
    def get_voices(self):
        """Get available voices from ElevenLabs API"""
        try:
            url = f"{self.api_url}/voices"
            headers = {
                "xi-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Error getting voices: {e}")
            return None
    
    def start_voice_agent_session(self, user_id):
        """Start a new voice agent session for health questionnaire"""
        try:
            url = f"{self.api_url}/agents/{self.agent_id}/sessions"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Create a session with initial context
            data = {
                "user_id": user_id,
                "context": {
                    "user_info": {
                        "user_id": user_id
                    },
                    "session_type": "health_questionnaire",
                    "question_count": 0,
                    "max_questions": 3,  # Limit to 3 questions
                    "responses": {}
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                session_data = response.json()
                print(f"Voice agent session created: {session_data}")
                return session_data
            else:
                print(f"ElevenLabs Agent API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error starting voice agent session: {e}")
            return None
    
    def send_audio_to_agent(self, session_id, audio_file):
        """Send audio to the voice agent and get a response"""
        try:
            url = f"{self.api_url}/agents/{self.agent_id}/sessions/{session_id}/audio"
            headers = {
                "xi-api-key": self.api_key
            }
            
            # Create a multipart form with the audio file
            files = {
                'audio': (audio_file.filename, audio_file, 'audio/wav')
            }
            
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                # Save audio response to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_path = temp_file.name
                    temp_file.write(response.content)
                
                return temp_path
            else:
                print(f"ElevenLabs Agent API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error sending audio to agent: {e}")
            return None
    
    def send_text_to_agent(self, session_id, text_input):
        """Send text to the voice agent and get a response"""
        try:
            url = f"{self.api_url}/agents/{self.agent_id}/sessions/{session_id}/text"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text_input
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                # Save audio response to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_path = temp_file.name
                    temp_file.write(response.content)
                
                return temp_path
            else:
                print(f"ElevenLabs Agent API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error sending text to agent: {e}")
            return None
    
    def get_session_history(self, session_id):
        """Get the conversation history for a voice agent session"""
        try:
            url = f"{self.api_url}/agents/{self.agent_id}/sessions/{session_id}/history"
            headers = {
                "xi-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                history_data = response.json()
                print(f"Voice agent history retrieved: {history_data}")
                return history_data
            else:
                print(f"ElevenLabs Agent API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting session history: {e}")
            return None
    
    def check_session_status(self, session_id):
        """Check if the voice agent session is complete"""
        try:
            url = f"{self.api_url}/agents/{self.agent_id}/sessions/{session_id}"
            headers = {
                "xi-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                session_data = response.json()
                
                # Check if we've reached the maximum number of questions
                context = session_data.get('context', {})
                question_count = context.get('question_count', 0)
                max_questions = context.get('max_questions', 3)
                
                is_complete = question_count >= max_questions
                
                return {
                    'is_complete': is_complete,
                    'question_count': question_count,
                    'max_questions': max_questions,
                    'context': context
                }
            else:
                print(f"ElevenLabs Agent API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error checking session status: {e}")
            return None
    
    def update_session_context(self, session_id, context_updates):
        """Update the context of a voice agent session"""
        try:
            url = f"{self.api_url}/agents/{self.agent_id}/sessions/{session_id}/context"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "context": context_updates
            }
            
            response = requests.patch(url, headers=headers, json=data)
            
            if response.status_code == 200:
                updated_context = response.json()
                print(f"Voice agent context updated: {updated_context}")
                return updated_context
            else:
                print(f"ElevenLabs Agent API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error updating session context: {e}")
            return None
    
    def format_conversation_for_anthropic(self, session_history):
        """Format the conversation history for Anthropic input"""
        if not session_history or 'turns' not in session_history:
            return "No conversation history available."
        
        formatted_conversation = "Health Questionnaire Conversation:\n\n"
        
        for turn in session_history.get('turns', []):
            if turn.get('role') == 'agent':
                formatted_conversation += f"Healthcare Assistant: {turn.get('content', '')}\n\n"
            elif turn.get('role') == 'user':
                formatted_conversation += f"Patient: {turn.get('content', '')}\n\n"
        
        # Extract structured health data
        context = session_history.get('context', {})
        responses = context.get('responses', {})
        
        formatted_conversation += "\nStructured Health Data:\n"
        for question, answer in responses.items():
            formatted_conversation += f"- {question}: {answer}\n"
        
        return formatted_conversation