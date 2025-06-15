import logging
from typing import Optional
import httpx
import os
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered features"""
    
    def __init__(self):
        """Initialize the AI service"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY environment variable not set")
    
    async def generate_explanation(
        self,
        quiz_title: str,
        quiz_level: str,
        question_text: str,
        correct_answer_text: str,
        student_answer_text: Optional[str] = None,
        is_student_correct: bool = False
    ) -> str:
        """
        Generate an explanation for a quiz answer using AI
        
        Args:
            quiz_title: Title of the quiz
            quiz_level: Level of the quiz (e.g., "Beginner", "Intermediate")
            question_text: Text of the question
            correct_answer_text: Text of the correct answer
            student_answer_text: Text of the student's answer (if different from correct)
            is_student_correct: Whether the student's answer was correct
            
        Returns:
            Generated explanation text
            
        Raises:
            HTTPException: If there's an error with the AI service
        """
        try:
            # Check if API key is available
            if not self.api_key:
                logger.error("Cannot generate explanation: OPENAI_API_KEY not set")
                return "Explanation not available. Please contact an administrator."
            
            # Build the prompt based on whether the student was correct
            if is_student_correct:
                prompt = (
                    f"You are an educational assistant explaining quiz answers.\n\n"
                    f"Quiz: {quiz_title} (Level: {quiz_level})\n"
                    f"Question: {question_text}\n"
                    f"Correct answer: {correct_answer_text}\n\n"
                    f"The student answered correctly. Provide a brief (2-3 sentences) explanation "
                    f"of why this answer is correct. Use simple language appropriate for the quiz level."
                )
            else:
                prompt = (
                    f"You are an educational assistant explaining quiz answers.\n\n"
                    f"Quiz: {quiz_title} (Level: {quiz_level})\n"
                    f"Question: {question_text}\n"
                    f"Correct answer: {correct_answer_text}\n"
                    f"Student's answer: {student_answer_text}\n\n"
                    f"The student answered incorrectly. Provide a brief (2-3 sentences) explanation "
                    f"of why the correct answer is right and where the student's answer went wrong. "
                    f"Use simple language appropriate for the quiz level."
                )
            
            # Prepare API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            # Make API call with timeout
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0  # 10 second timeout
                )
                
                response_data = response.json()
                
                if response.status_code != 200:
                    logger.error(f"AI service error: {response_data}")
                    return "Explanation not available due to a service error."
                
                # Extract explanation from response
                explanation = response_data["choices"][0]["message"]["content"].strip()
                return explanation
                
        except httpx.TimeoutException:
            logger.error("AI service timeout")
            return "Explanation not available due to service timeout."
            
        except Exception as e:
            logger.exception(f"Error generating explanation: {str(e)}")
            return "Explanation not available due to an unexpected error." 