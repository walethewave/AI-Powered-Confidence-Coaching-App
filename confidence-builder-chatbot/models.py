from typing import List, Dict, Optional
from datetime import datetime
import json
from pydantic import BaseModel, Field, validator

class UserMessage(BaseModel):
    """User message with validation"""
    content: str = Field(..., min_length=1, max_length=1000, description="User's message content")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="ISO format timestamp")

    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ConfidenceAssessment(BaseModel):
    """Assessment results from AI analysis"""
    confidence_level: int = Field(..., ge=1, le=10, description="Confidence level 1-10")
    emotional_state: str = Field(..., description="Current emotional state")
    main_challenge: str = Field(..., description="Primary challenge they're facing")
    hidden_strengths: str = Field(..., description="Strengths they might not see")
    best_approach: str = Field(..., description="Most effective coaching approach")

    @classmethod
    def from_json_string(cls, json_string: str):
        """Parse JSON response from AI"""
        try:
            data = json.loads(json_string)
            return cls(**data)
        except (json.JSONDecodeError, ValueError) as e:
            return cls(
                confidence_level=5,
                emotional_state="uncertain",
                main_challenge="general confidence",
                hidden_strengths="resilience and self-awareness",
                best_approach="supportive encouragement"
            )

class AIResponse(BaseModel):
    """Complete AI response with all components"""
    response: str = Field(..., description="Main conversational response")
    confidence_level: int = Field(..., ge=1, le=10)
    confidence_tips: List[str] = Field(default=[], description="Actionable confidence tips")
    next_steps: List[str] = Field(default=[], description="Specific next actions")
    assessment: Optional[ConfidenceAssessment] = None
    matched_keywords: List[str] = Field(default=[], description="Keywords used for confidence assessment")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="ISO format timestamp")

    def extract_tips_and_steps(self):
        """Extract tips and steps from response text if not provided separately"""
        if not self.confidence_tips:
            lines = self.response.split('\n')
            tips = []
            steps = []
            
            for line in lines:
                clean_line = line.strip()
                if clean_line.startswith(('1.', '2.', '3.', '•', '-', '→')):
                    if any(word in clean_line.lower() for word in ['try', 'practice', 'do', 'start']):
                        steps.append(clean_line.lstrip('123456789.•-→ '))
                    else:
                        tips.append(clean_line.lstrip('123456789.•-→ '))
            
            self.confidence_tips = tips[:3]
            self.next_steps = steps[:3]

class ChatSession(BaseModel):
    """Track entire chat session data"""
    messages: List[dict] = Field(default=[])
    confidence_history: List[int] = Field(default=[])
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="ISO format start time")
    total_messages: int = Field(default=0)

    def add_message(self, role: str, content: str, confidence_level: Optional[int] = None, matched_keywords: List[str] = None, timestamp: str = None):
        """Add a message to the session with optional timestamp and keywords"""
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp or datetime.now().isoformat()
        }
        if role == "assistant":
            message["confidence_level"] = confidence_level
            message["matched_keywords"] = matched_keywords or []
        self.messages.append(message)
        self.total_messages += 1
        
        if confidence_level and role == "assistant":
            self.confidence_history.append(confidence_level)

    def get_average_confidence(self) -> float:
        """Calculate average confidence level"""
        if not self.confidence_history:
            return 5.0
        return round(sum(self.confidence_history) / len(self.confidence_history), 1)

    def get_confidence_trend(self) -> List[int]:
        """Get confidence levels for charting"""
        if len(self.confidence_history) < 2:
            return [5, 6]
        return self.confidence_history[-10:]

    class Config:
        extra = "allow"

    def get_session_summary(self) -> dict:
        """Get session analytics"""
        return {
            "total_messages": self.total_messages,
            "average_confidence": self.get_average_confidence(),
            "confidence_trend": self.get_confidence_trend(),
            "session_duration": str(datetime.now() - datetime.fromisoformat(self.start_time)).split('.')[0],
            "latest_confidence": self.confidence_history[-1] if self.confidence_history else 5
        }

class PromptData(BaseModel):
    """Structure for organizing prompt data"""
    system_prompt: str
    user_message: str
    confidence_level: int
    context: str = ""

    class Config:
        extra = "allow"