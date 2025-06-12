import json
import logging
from typing import Dict, List, Optional, Tuple
import openai

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIQuizGeneratorService:
    """Service for generating quizzes using AI"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the service with optional API key"""
        self.api_key = openai_api_key or settings.OPENAI_API_KEY
        openai.api_key = self.api_key
    
    async def generate_quiz(self, topic: str, question_count: int, level_data: Dict) -> Tuple[List, str]:
        """
        Generate a quiz using OpenAI's GPT model
        
        Args:
            topic: The topic of the quiz
            question_count: Number of questions to generate
            level_data: Dictionary containing level information
            
        Returns:
            Tuple containing list of questions with answers and the quiz title
        """
        prompt = self._create_prompt(topic, question_count, level_data)
        
        try:
            response = await self._call_openai_api(prompt)
            parsed_data = self._parse_response(response)
            return parsed_data
        except Exception as e:
            logger.error(f"Error generating quiz with AI: {str(e)}")
            raise AIGenerationError(f"Failed to generate quiz: {str(e)}")
    
    def _create_prompt(self, topic: str, question_count: int, level_data: Dict) -> str:
        """
        Create a prompt for the AI model
        
        Args:
            topic: The topic of the quiz
            question_count: Number of questions to generate
            level_data: Dictionary containing level information
            
        Returns:
            String containing the prompt for the AI model
        """
        level_description = level_data.get("description", "")
        level_code = level_data.get("code", "")
        
        return f"""
        You are an educational quiz generator. Your task is to create a quiz on the topic: "{topic}".

        The difficulty level is "{level_description}" (code: {level_code}).
        
        Generate {question_count} questions with 4 answer options for each question. 
        Exactly one answer should be correct for each question.
        
        For each question:
        1. Make sure the questions test understanding, not just memorization
        2. Ensure questions are clear and unambiguous
        3. Provide 4 answer options that are plausible but only one is correct
        
        Return the result in JSON format with the following structure:
        {{
            "title": "Quiz title related to the topic",
            "questions": [
                {{
                    "text": "Question text",
                    "answers": [
                        {{"text": "Answer option 1", "is_correct": true/false}},
                        {{"text": "Answer option 2", "is_correct": true/false}},
                        {{"text": "Answer option 3", "is_correct": true/false}},
                        {{"text": "Answer option 4", "is_correct": true/false}}
                    ]
                }}
            ]
        }}
        
        Each question MUST have exactly ONE correct answer (is_correct: true).
        """
    
    async def _call_openai_api(self, prompt: str) -> str:
        """
        Call the OpenAI API to generate quiz content
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            String containing the API response content
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an educational quiz generator AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise AIGenerationError(f"OpenAI API call failed: {str(e)}")
    
    def _parse_response(self, response: str) -> Tuple[List, str]:
        """
        Parse the response from the AI model
        
        Args:
            response: The response from the AI model
            
        Returns:
            Tuple containing list of questions with answers and the quiz title
        """
        try:
            # Clean up the response to ensure it's valid JSON
            # Sometimes the API returns markdown code blocks or extra text
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            
            data = json.loads(json_str)
            
            # Validate structure
            if "title" not in data or "questions" not in data:
                raise ValueError("Response missing required fields (title or questions)")
            
            questions = data["questions"]
            for i, question in enumerate(questions):
                if "text" not in question or "answers" not in question:
                    raise ValueError(f"Question {i+1} missing required fields")
                
                # Ensure exactly one correct answer
                correct_count = sum(1 for a in question["answers"] if a.get("is_correct"))
                if correct_count != 1:
                    raise ValueError(f"Question {i+1} has {correct_count} correct answers, must have exactly 1")
                
                # Ensure 4 answer options
                if len(question["answers"]) != 4:
                    raise ValueError(f"Question {i+1} has {len(question['answers'])} answers, must have exactly 4")
            
            return questions, data["title"]
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            raise AIGenerationError(f"Invalid JSON in AI response: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid AI response structure: {str(e)}")
            raise AIGenerationError(f"Invalid quiz structure: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            raise AIGenerationError(f"Error parsing AI response: {str(e)}")


class AIGenerationError(Exception):
    """Exception raised for errors in the AI generation process"""
    pass 