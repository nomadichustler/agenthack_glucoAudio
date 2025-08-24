import os
import anthropic
import json
from datetime import datetime
from app.services.prompt_templates import (
    QUESTIONNAIRE_SYSTEM_PROMPT,
    QUESTIONNAIRE_USER_PROMPT,
    RECORDING_PROMPT_SYSTEM,
    RECORDING_PROMPT_USER_TEMPLATE,
    HEALTH_CONTEXT_SYSTEM,
    HEALTH_CONTEXT_USER_TEMPLATE,
    FALLBACK_QUESTIONNAIRE,
    FALLBACK_RECORDING_PROMPT,
    FALLBACK_HEALTH_CONTEXT,
    ERROR_MESSAGES
)

class ClaudeSonnetService:
    """Service for interacting with Claude 3.7 Sonnet API for questionnaire generation"""
    
    def __init__(self):
        """Initialize the Claude Sonnet service"""
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
            
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-7-sonnet-20250219"
    
    def generate_questionnaire(self):
        """Generate a dynamic health questionnaire with Claude 3.7 Sonnet"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,  # Claude 3.7 Sonnet supports larger context
                system=QUESTIONNAIRE_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": QUESTIONNAIRE_USER_PROMPT}
                ]
            )
            
            # Extract JSON from the response
            content = response.content[0].text
            
            # Find JSON in the response
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback questionnaire if JSON parsing fails
                print("Failed to parse JSON from questionnaire response")
                return FALLBACK_QUESTIONNAIRE
                
        except Exception as e:
            print(f"Error generating questionnaire with Claude Sonnet: {e}")
            return FALLBACK_QUESTIONNAIRE
    
    def generate_recording_prompt(self, questionnaire_responses):
        """Generate a text prompt for the user to read during voice recording"""
        try:
            # Format the user prompt with questionnaire responses
            user_prompt = RECORDING_PROMPT_USER_TEMPLATE.format(
                questionnaire_responses=json.dumps(questionnaire_responses, indent=2)
            )
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,  # Claude 3.7 Sonnet supports larger context
                system=RECORDING_PROMPT_SYSTEM,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Get the raw text
            raw_text = response.content[0].text.strip()
            
            # Sanitize the text
            sanitized_text = self._sanitize_text(raw_text)
            
            # Return the sanitized text
            return sanitized_text
                
        except Exception as e:
            print(f"Error generating recording prompt with Claude Sonnet: {e}")
            return FALLBACK_RECORDING_PROMPT
            
    def _sanitize_text(self, text):
        """Sanitize text to remove HTML entities and fix common issues"""
        if not text:
            return ""
            
        # Replace HTML entities
        replacements = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": "\"",
            "&#39;": "'",
            "&#x27;": "'",
            "&#x2F;": "/",
            "\n": " ",  # Replace newlines with spaces
            "\r": "",   # Remove carriage returns
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Remove any double spaces
        while "  " in text:
            text = text.replace("  ", " ")
            
        return text
    
    def analyze_responses(self, questionnaire_responses, voice_text=None):
        """Analyze questionnaire responses to extract health context"""
        try:
            # Sanitize voice text if provided
            sanitized_voice_text = self._sanitize_text(voice_text) if voice_text else None
            
            # Format the user prompt with questionnaire responses and voice text if available
            voice_text_context = f"The user also recorded themselves saying: '{sanitized_voice_text}'" if sanitized_voice_text else ""
            
            user_prompt = HEALTH_CONTEXT_USER_TEMPLATE.format(
                questionnaire_responses=json.dumps(questionnaire_responses, indent=2),
                voice_text_context=voice_text_context
            )
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,  # Claude 3.7 Sonnet supports larger context
                system=HEALTH_CONTEXT_SYSTEM,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract JSON from the response
            content = response.content[0].text
            
            # Find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                # Sanitize any text fields in the result
                if result.get('notes'):
                    result['notes'] = self._sanitize_text(result['notes'])
                    
                return result
            else:
                # Fallback analysis if JSON parsing fails
                print("Failed to parse JSON from health context response")
                return FALLBACK_HEALTH_CONTEXT
                
        except Exception as e:
            print(f"Error analyzing responses with Claude Sonnet: {e}")
            return FALLBACK_HEALTH_CONTEXT
