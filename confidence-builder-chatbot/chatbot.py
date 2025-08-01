import google.generativeai as genai
import os
import json
import logging
import requests
from typing import Optional, Tuple
from datetime import datetime
from models import UserMessage, AIResponse, ConfidenceAssessment, ChatSession, PromptData
from prompts import ConfidencePromptEngine
from dotenv import load_dotenv
import streamlit as st
from typing import List
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfidenceChatbot:
    """
    Main chatbot class that handles confidence coaching conversations with Gemini AI and motivational quotes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the chatbot with Gemini AI"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.session = ChatSession()
        self.prompt_engine = ConfidencePromptEngine()
        
        logger.info("ConfidenceChatbot initialized successfully")
    
    def get_motivational_quote(self) -> str:
        """Fetch a motivational quote from an external API"""
        try:
            response = requests.get("https://type.fit/api/quotes")
            if response.status_code == 200:
                quotes = response.json()
                import random
                return random.choice(quotes)["text"]
            return "Stay strong, you’ve got this!"
        except Exception as e:
            logger.error(f"Failed to fetch quote: {str(e)}")
            return "Stay strong, you’ve got this!"
    
    def _make_ai_request(self, prompt: str, max_retries: int = 3) -> str:
        """Make request to Gemini AI with error handling"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.warning(f"AI request attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return self._get_fallback_response()
        return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback response when AI fails"""
        return """I hear you, and I want you to know that reaching out takes courage. 🌟

While I'm having a technical moment, here's what I want you to remember: every challenge you're facing right now is temporary, but your strength is permanent.

Take a deep breath. You've overcome difficulties before, and you have everything within you to handle whatever comes next.

What's one small thing you can do today to take care of yourself, make sure you do it till I'm back online?"""
    
    def _assess_confidence(self, user_message: str) -> ConfidenceAssessment:
        """Analyze user message for confidence indicators"""
        # Prioritize keyword-based assessment for user input
        confidence_level, matched_keywords = self._extract_confidence_from_text(user_message)
        
        try:
            assessment_prompt = self.prompt_engine.get_confidence_assessment_prompt(user_message)
            response = self._make_ai_request(assessment_prompt)
            
            if response.strip().startswith('{'):
                assessment = ConfidenceAssessment.from_json_string(response)
                # Use keyword-based confidence level if lower (indicating stronger signal)
                if confidence_level < assessment.confidence_level:
                    assessment.confidence_level = confidence_level
                return assessment
            else:
                return ConfidenceAssessment(
                    confidence_level=confidence_level,
                    emotional_state="processing",
                    main_challenge="general confidence",
                    hidden_strengths="self-awareness and courage to reach out",
                    best_approach="supportive encouragement"
                )
        except Exception as e:
            logger.error(f"Assessment failed: {str(e)}")
            return ConfidenceAssessment(
                confidence_level=confidence_level,
                emotional_state="uncertain",
                main_challenge="unknown",
                hidden_strengths="resilience",
                best_approach="gentle support"
            )
    
    def _extract_confidence_from_text(self, text: str) -> Tuple[int, List[str]]:
        """Extract confidence level and matched keywords from text response"""
        import re
        numbers = re.findall(r'\b([1-9]|10)\b', text)
        matched_keywords = []
        
        if numbers:
            return int(numbers[0]), matched_keywords
        
        text_lower = text.lower().strip()
        if any(word in text_lower for word in ['very low', 'terrible', 'awful', 'hopeless', 'depressed', 'dumb', 'useless', 'sad']):
            matched_keywords.extend([word for word in ['very low', 'terrible', 'awful', 'hopeless', 'depressed', 'dumb', 'useless', 'sad'] if word in text_lower])
            return 2, matched_keywords
        elif any(word in text_lower for word in ['low', 'down', 'struggling', 'difficult', 'tired']):
            matched_keywords.extend([word for word in ['low', 'down', 'struggling', 'difficult', 'tired'] if word in text_lower])
            return 4, matched_keywords
        elif any(word in text_lower for word in ['okay', 'fine', 'average', 'neutral']):
            matched_keywords.extend([word for word in ['okay', 'fine', 'average', 'neutral'] if word in text_lower])
            return 5, matched_keywords
        elif any(word in text_lower for word in ['good', 'positive', 'better', 'confident']):
            matched_keywords.extend([word for word in ['good', 'positive', 'better', 'confident'] if word in text_lower])
            return 7, matched_keywords
        elif any(word in text_lower for word in ['great', 'excellent', 'amazing', 'fantastic']):
            matched_keywords.extend([word for word in ['great', 'excellent', 'amazing', 'fantastic'] if word in text_lower])
            return 9, matched_keywords
        return 5, matched_keywords
    
    def generate_response(self, user_message: UserMessage) -> AIResponse:
        """Generate a complete confidence coaching response"""
        try:
            user_input = user_message.content.lower()
            
            if "motivate me" in user_input:
                quote = self.get_motivational_quote()
                ai_response = AIResponse(
                    response=f"Here's something to lift you up: \"{quote}\"",
                    confidence_level=5,
                    assessment=ConfidenceAssessment(
                        confidence_level=5,
                        emotional_state="motivated",
                        main_challenge="seeking inspiration",
                        hidden_strengths="openness to encouragement",
                        best_approach="positive reinforcement"
                    ),
                    matched_keywords=["motivate"],
                    timestamp=datetime.now().isoformat()
                )
                ai_response.extract_tips_and_steps()
                self.session.add_message("user", user_message.content, timestamp=user_message.timestamp)
                self.session.add_message("assistant", ai_response.response, ai_response.confidence_level, matched_keywords=["motivate"], timestamp=ai_response.timestamp)
                return ai_response
            
            assessment = self._assess_confidence(user_message.content)
            confidence_level, matched_keywords = self._extract_confidence_from_text(user_message.content)
            
            if assessment.confidence_level < 4:
                quote = self.get_motivational_quote()
                assessment.best_approach += f" Here's a quote to inspire you: \"{quote}\""
            
            context = self._build_context()
            response_prompt = self.prompt_engine.get_response_prompt(
                user_message.content,
                assessment.confidence_level,
                context
            )
            
            full_prompt = f"""
            {self.prompt_engine.get_system_prompt()}
            
            {response_prompt}
            """
            
            ai_response_text = self._make_ai_request(full_prompt)
            
            ai_response = AIResponse(
                response=ai_response_text,
                confidence_level=assessment.confidence_level,
                assessment=assessment,
                matched_keywords=matched_keywords,
                timestamp=datetime.now().isoformat()
            )
            
            ai_response.extract_tips_and_steps()
            
            self.session.add_message("user", user_message.content, timestamp=user_message.timestamp)
            self.session.add_message("assistant", ai_response.response, ai_response.confidence_level, matched_keywords=matched_keywords, timestamp=ai_response.timestamp)
            
            logger.info(f"Generated response for confidence level: {assessment.confidence_level}")
            return ai_response
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            fallback_response = AIResponse(
                response=self._get_fallback_response(),
                confidence_level=5,
                confidence_tips=[
                    "Take one small step forward today",
                    "Remember that setbacks are temporary",
                    "You're stronger than you think"
                ],
                next_steps=[
                    "Practice deep breathing for 2 minutes",
                    "Write down one thing you're grateful for",
                    "Reach out to someone who supports you"
                ],
                matched_keywords=[],
                timestamp=datetime.now().isoformat()
            )
            self.session.add_message("user", user_message.content, timestamp=user_message.timestamp)
            self.session.add_message("assistant", fallback_response.response, 5, matched_keywords=[], timestamp=fallback_response.timestamp)
            return fallback_response
    
    def _build_context(self) -> str:
        """Build context from recent conversation history"""
        if len(self.session.messages) < 2:
            return "This is the beginning of our conversation."
        
        recent_messages = self.session.messages[-4:]
        context_parts = []
        
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "You"
            context_parts.append(f"{role}: {msg['content'][:100]}...")
        
        return "Recent conversation context:\n" + "\n".join(context_parts)
    
    def get_session_summary(self) -> dict:
        """Get current session analytics"""
        return self.session.get_session_summary()
    
    def reset_session(self):
        """Reset the chat session"""
        self.session = ChatSession()
        logger.info("Session reset")
    
    def get_confidence_history(self) -> list:
        """Get confidence level history for charting"""
        return self.session.get_confidence_trend()
    
    def export_session(self) -> dict:
        """Export session data for analysis"""
        return {
            "session_summary": self.get_session_summary(),
            "full_conversation": self.session.messages,
            "confidence_progression": self.session.confidence_history
        }