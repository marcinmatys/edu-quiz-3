import logging
from typing import Optional
import os
from openai import OpenAI, AsyncOpenAI

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered features"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the AI service"""
        self.api_key = openai_api_key or settings.OPENAI_API_KEY
        logger.info(f"OpenAI API key: {self.api_key}")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.sync_client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4.1"
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set in environment or settings")
    
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
                    f"of why this answer is correct. You may refer to relevant rules, principles, or facts if helpful. "
                    f"Use simple language appropriate for the quiz level."
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
                    f"You may refer to relevant rules, principles, or facts if helpful. "
                    f"Use simple language appropriate for the quiz level."
                )
            
            try:
                # Try async call first
                response = await self._call_openai_api(prompt)
                return response.strip()
            except Exception as e:
                logger.warning(f"Async API call failed, trying synchronous fallback: {str(e)}")
                try:
                    # Fallback to synchronous call
                    response = self._call_openai_api_sync(prompt)
                    return response.strip()
                except Exception as e:
                    logger.error(f"Error generating explanation with AI: {str(e)}")
                    return "Explanation not available due to an unexpected error."
                
        except Exception as e:
            logger.exception(f"Error generating explanation: {str(e)}")
            return "Explanation not available due to an unexpected error."
    
    async def _call_openai_api(self, prompt: str) -> str:
        """
        Call the OpenAI API to generate explanation
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            String containing the API response content
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an educational assistant explaining quiz answers."},
                {"role": "user", "content": prompt}
            ],
            timeout=10.0,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    
    def _call_openai_api_sync(self, prompt: str) -> str:
        """
        Call the OpenAI API synchronously to generate explanation
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            String containing the API response content
        """
        response = self.sync_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an educational assistant explaining quiz answers."},
                {"role": "user", "content": prompt}
            ],
            timeout=10.0,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content 