"""
AI Service for OpenAI integration and medical assistance
"""
import openai
from typing import List, Dict, Optional
from datetime import datetime
import time
from ..config import Config


class AIService:
    """Service for AI-powered medical assistance using OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        openai.api_key = Config.OPENAI_API_KEY
        self.model = "gpt-4"  # Use GPT-4 for medical accuracy
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def generate_chat_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        medical_context: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate AI response for user message
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in conversation
            medical_context: Additional medical knowledge context
        
        Returns:
            Dict with response, tokens used, and metadata
        """
        # Build messages for OpenAI API
        messages = self._build_messages(
            user_message,
            conversation_history,
            medical_context
        )
        
        # Call OpenAI API with retry logic
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,  # Balanced creativity and consistency
                    max_tokens=500,   # Limit response length
                    top_p=0.9,
                    frequency_penalty=0.3,
                    presence_penalty=0.3
                )
                
                elapsed_time = time.time() - start_time
                
                # Extract response
                ai_message = response.choices[0].message.content
                
                # Add medical disclaimer
                ai_message_with_disclaimer = self._add_medical_disclaimer(ai_message)
                
                return {
                    'response': ai_message_with_disclaimer,
                    'original_response': ai_message,
                    'tokens_used': response.usage.total_tokens,
                    'response_time': elapsed_time,
                    'model': self.model,
                    'finish_reason': response.choices[0].finish_reason
                }
                
            except openai.error.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise Exception(f"OpenAI rate limit exceeded: {str(e)}")
            
            except openai.error.APIError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise Exception(f"OpenAI API error: {str(e)}")
            
            except Exception as e:
                raise Exception(f"Error generating AI response: {str(e)}")
    
    def _build_messages(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        medical_context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build message array for OpenAI API
        
        Args:
            user_message: Current user message
            conversation_history: Previous messages
            medical_context: Medical knowledge context
        
        Returns:
            List of message dicts for OpenAI
        """
        messages = []
        
        # System message with role definition
        system_message = self._get_system_prompt(medical_context)
        messages.append({
            'role': 'system',
            'content': system_message
        })
        
        # Add conversation history (limit to last 10 messages for context window)
        if conversation_history:
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Add current user message
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        return messages
    
    def _get_system_prompt(self, medical_context: Optional[str] = None) -> str:
        """
        Get system prompt that defines AI assistant behavior
        
        Args:
            medical_context: Additional medical knowledge
        
        Returns:
            System prompt string
        """
        base_prompt = """You are a helpful AI medical assistant for a patient support platform. Your role is to:

1. Provide general health information and guidance
2. Explain medical conditions in simple, patient-friendly language
3. Help patients understand their treatment plans
4. Answer questions about medications and lab results
5. Encourage healthy lifestyle choices

IMPORTANT GUIDELINES:
- Always use simple, non-technical language
- Be empathetic and supportive
- Never provide specific medical diagnoses
- Always recommend consulting healthcare professionals for medical decisions
- Emphasize that you provide information, not medical advice
- If asked about emergencies, immediately advise calling emergency services
- Respect patient privacy and confidentiality

LIMITATIONS:
- You cannot prescribe medications
- You cannot diagnose conditions
- You cannot replace professional medical care
- You cannot access real-time medical records (only what's shared in conversation)
"""
        
        if medical_context:
            base_prompt += f"\n\nRELEVANT MEDICAL INFORMATION:\n{medical_context}"
        
        return base_prompt
    
    def _add_medical_disclaimer(self, message: str) -> str:
        """
        Add medical disclaimer to AI response
        
        Args:
            message: Original AI message
        
        Returns:
            Message with disclaimer
        """
        # Check if message already has disclaimer
        if "medical advice" in message.lower() or "consult" in message.lower():
            return message
        
        # Add disclaimer for medical-related responses
        medical_keywords = [
            'symptom', 'disease', 'condition', 'treatment', 'medication',
            'diagnosis', 'pain', 'fever', 'infection', 'doctor', 'hospital'
        ]
        
        is_medical = any(keyword in message.lower() for keyword in medical_keywords)
        
        if is_medical:
            disclaimer = "\n\n⚕️ *Please note: This information is for educational purposes only and does not constitute medical advice. Always consult with a qualified healthcare professional for medical decisions.*"
            return message + disclaimer
        
        return message
    
    def check_for_emergency(self, message: str) -> bool:
        """
        Check if message indicates a medical emergency
        
        Args:
            message: User message
        
        Returns:
            True if emergency keywords detected
        """
        emergency_keywords = [
            'chest pain', 'heart attack', 'stroke', 'can\'t breathe',
            'difficulty breathing', 'severe bleeding', 'unconscious',
            'suicide', 'overdose', 'severe pain', 'emergency'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in emergency_keywords)
    
    def get_emergency_response(self) -> str:
        """
        Get emergency response message
        
        Returns:
            Emergency guidance message
        """
        return """🚨 **EMERGENCY ALERT** 🚨

Based on your message, this may be a medical emergency.

**IMMEDIATE ACTIONS:**
1. Call emergency services (911 in US) immediately
2. Do not wait for a response from this app
3. If safe, go to the nearest emergency room
4. Have someone stay with you if possible

This AI assistant cannot handle medical emergencies. Please seek immediate professional medical help.

If you're experiencing a mental health crisis, contact:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741

Your safety is the top priority. Please get help now."""
