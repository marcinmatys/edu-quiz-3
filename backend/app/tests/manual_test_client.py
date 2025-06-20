#!/usr/bin/env python
import httpx
import asyncio
import json
import sys
from typing import Dict, Any, Optional


class APIClient:
    """Simple HTTP client for testing the Quizzes API endpoint"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    async def login(self, username: str, password: str) -> bool:
        """Login to get authentication token"""
        url = f"{self.base_url}/api/v1/auth/token"
        data = {
            "username": username,
            "password": password
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, 
                    data={"username": username, "password": password},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                token_data = response.json()
                self.token = token_data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"Login successful for user: {username}")
                return True
            except httpx.HTTPStatusError as e:
                print(f"Login failed: {e}")
                return False
    
    async def get_quizzes(
        self, 
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of quizzes with optional sorting and filtering
        
        Args:
            sort_by: Field to sort by (level, title, updated_at)
            order: Sort order (asc, desc)
            status: Filter by status (draft, published) - admin only
        """
        url = f"{self.base_url}/api/v1/quizzes/"
        
        # Build query parameters
        params = {}
        if sort_by:
            params["sort_by"] = sort_by
        if order:
            params["order"] = order
        if status:
            params["status"] = status
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Error getting quizzes: {e}")
                return {"error": str(e)}
    
    async def create_quiz(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quiz with AI generation"""
        url = f"{self.base_url}/api/v1/quizzes/"
        
        # Use a longer timeout (120 seconds) for quiz creation since AI generation can take time
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                print("Sending request to create quiz. This may take some time due to AI generation...")
                response = await client.post(
                    url,
                    json=quiz_data,
                    headers=self.headers
                )
                print(f"Response status code: {response.status_code}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Error creating quiz: {e}")
                if e.response:
                    print(f"Response: {e.response.text}")
                return {"error": str(e)}
            except httpx.ReadTimeout:
                print("Request timed out. The quiz generation is taking longer than expected.")
                print("The quiz may still be created in the background.")
                return {"error": "Request timed out. The operation might still be processing."}
    
    async def get_quiz(self, quiz_id: int) -> Dict[str, Any]:
        """Get a specific quiz by ID"""
        url = f"{self.base_url}/api/v1/quizzes/{quiz_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Error getting quiz {quiz_id}: {e}")
                return {"error": str(e)}
    
    async def edit_quiz(self, quiz_id: int, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Edit an existing quiz by ID"""
        url = f"{self.base_url}/api/v1/quizzes/{quiz_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    url,
                    json=quiz_data,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Error editing quiz {quiz_id}: {e}")
                if e.response:
                    print(f"Response: {e.response.text}")
                return {"error": str(e)}

    async def delete_quiz(self, quiz_id: int) -> Dict[str, Any]:
        """Delete a quiz by ID"""
        url = f"{self.base_url}/api/v1/quizzes/{quiz_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(url, headers=self.headers)
                response.raise_for_status()
                return {"success": True, "message": f"Quiz {quiz_id} deleted successfully"}
            except httpx.HTTPStatusError as e:
                print(f"Error deleting quiz {quiz_id}: {e}")
                if e.response:
                    print(f"Response: {e.response.text}")
                return {"error": str(e)}


async def main():
    """Main function to run the API client"""
    client = APIClient()
    
    # Login first (you need to have a valid admin user)
    if len(sys.argv) > 2:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = input("Enter username: ")
        password = input("Enter password: ")
    
    logged_in = await client.login(username, password)
    if not logged_in:
        print("Login failed. Cannot proceed.")
        return
    
    # Simple menu system
    while True:
        print("\n--- Quiz API Testing Menu ---")
        print("1. Get all quizzes")
        print("2. Get quizzes with sorting and filtering")
        print("3. Create a new quiz")
        print("4. Get quiz by ID")
        print("5. Edit quiz by ID")
        print("6. Delete quiz by ID")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            quizzes = await client.get_quizzes()
            print("\n--- Quiz List ---")
            print(json.dumps(quizzes, indent=2))
        
        elif choice == "2":
            print("\n--- Get Quizzes with Sorting and Filtering ---")
            sort_by = input("Sort by (level, title, updated_at) [default=level]: ").strip() or None
            order = input("Order (asc, desc) [default=asc]: ").strip() or None
            status = input("Status (draft, published) [admin only, leave empty for all]: ").strip() or None
            
            quizzes = await client.get_quizzes(sort_by=sort_by, order=order, status=status)
            print("\n--- Quiz List ---")
            print(json.dumps(quizzes, indent=2))
        
        elif choice == "3":
            print("\n--- Create New Quiz ---")
            topic = input("Enter quiz topic: ")
            
            try:
                question_count = int(input("Enter number of questions (5-20): "))
                if not (5 <= question_count <= 20):
                    print("Question count must be between 5 and 20.")
                    continue
            except ValueError:
                print("Invalid number.")
                continue
            
            try:
                level_id = int(input("Enter level ID: "))
            except ValueError:
                print("Invalid level ID.")
                continue
                
            quiz_data = {
                "topic": topic,
                "question_count": question_count,
                "level_id": level_id,
                "title": f"Quiz on {topic}"  # Note: AI will generate the actual title
            }
            
            print("\nCreating quiz...")
            result = await client.create_quiz(quiz_data)
            print("\n--- Created Quiz ---")
            print(json.dumps(result, indent=2))
        
        elif choice == "4":
            try:
                quiz_id = int(input("\nEnter quiz ID: "))
            except ValueError:
                print("Invalid quiz ID.")
                continue
                
            quiz = await client.get_quiz(quiz_id)
            print(f"\n--- Quiz {quiz_id} Details ---")
            print(json.dumps(quiz, indent=2))
            
        elif choice == "5":
            print("\n--- Edit Quiz ---")
            try:
                quiz_id = int(input("Enter quiz ID to edit: "))
            except ValueError:
                print("Invalid quiz ID.")
                continue
                
            # First get the current quiz data
            current_quiz = await client.get_quiz(quiz_id)
            if "error" in current_quiz:
                print(f"Could not retrieve quiz {quiz_id}. Cannot edit.")
                continue
                
            print("\nCurrent quiz details:")
            print(json.dumps(current_quiz, indent=2))
            
            print("\n--- Edit Options ---")
            print("1. Edit quiz properties (title, status)")
            print("2. Edit a specific question")
            print("3. Edit a specific answer")
            
            edit_choice = input("\nEnter your choice: ")
            
            # Initialize update data with required fields from current quiz
            update_data = {
                "level_id": current_quiz.get("level_id"),
                "questions": current_quiz.get("questions", [])
            }
            
            if edit_choice == "1":
                # Get updated fields for quiz properties
                print("\nEnter new values (leave empty to keep current values):")
                title = input(f"Title [{current_quiz.get('title', '')}]: ").strip()
                status = input(f"Status (draft/published) [{current_quiz.get('status', 'draft')}]: ").strip()
                
                # Update data with new values
                if title:
                    update_data["title"] = title
                else:
                    update_data["title"] = current_quiz.get("title", "")
                    
                if status:
                    update_data["status"] = status
                else:
                    update_data["status"] = current_quiz.get("status", "draft")
            
            elif edit_choice == "2":
                # Show available questions
                print("\nAvailable questions:")
                questions = current_quiz.get("questions", [])
                for i, question in enumerate(questions):
                    print(f"{i+1}. {question.get('text', '')}")
                
                try:
                    question_idx = int(input("\nEnter question number to edit: ")) - 1
                    if question_idx < 0 or question_idx >= len(questions):
                        print("Invalid question number.")
                        continue
                except ValueError:
                    print("Invalid number.")
                    continue
                
                # Get the question to edit
                question = questions[question_idx]
                question_id = question.get("id")
                
                # Get updated fields for question
                print("\nEnter new values (leave empty to keep current values):")
                question_text = input(f"Question text [{question.get('text', '')}]: ").strip()
                explanation = input(f"Explanation [{question.get('explanation', '')}]: ").strip()
                
                # Update the specific question in the questions list
                for i, q in enumerate(update_data["questions"]):
                    if q.get("id") == question_id:
                        if question_text:
                            update_data["questions"][i]["text"] = question_text
                        if explanation:
                            update_data["questions"][i]["explanation"] = explanation
                        break
                
                # Include title and status from current quiz
                update_data["title"] = current_quiz.get("title", "")
                update_data["status"] = current_quiz.get("status", "draft")
            
            elif edit_choice == "3":
                # Show available questions first
                print("\nSelect a question first:")
                questions = current_quiz.get("questions", [])
                for i, question in enumerate(questions):
                    print(f"{i+1}. {question.get('text', '')}")
                
                try:
                    question_idx = int(input("\nEnter question number: ")) - 1
                    if question_idx < 0 or question_idx >= len(questions):
                        print("Invalid question number.")
                        continue
                except ValueError:
                    print("Invalid number.")
                    continue
                
                # Get the question and its answers
                question = questions[question_idx]
                question_id = question.get("id")
                answers = question.get("answers", [])
                
                # Show available answers
                print("\nAvailable answers:")
                for i, answer in enumerate(answers):
                    print(f"{i+1}. {answer.get('text', '')}")
                
                try:
                    answer_idx = int(input("\nEnter answer number to edit: ")) - 1
                    if answer_idx < 0 or answer_idx >= len(answers):
                        print("Invalid answer number.")
                        continue
                except ValueError:
                    print("Invalid number.")
                    continue
                
                # Get the answer to edit
                answer = answers[answer_idx]
                answer_id = answer.get("id")
                
                # Get updated fields for answer
                print("\nEnter new values (leave empty to keep current values):")
                answer_text = input(f"Answer text [{answer.get('text', '')}]: ").strip()
                is_correct_input = input(f"Is correct (true/false) [{answer.get('is_correct', False)}]: ").strip().lower()
                
                is_correct = None
                if is_correct_input in ["true", "t", "yes", "y", "1"]:
                    is_correct = True
                elif is_correct_input in ["false", "f", "no", "n", "0"]:
                    is_correct = False
                
                # Update the specific answer in the questions list
                for i, q in enumerate(update_data["questions"]):
                    if q.get("id") == question_id:
                        for j, a in enumerate(q.get("answers", [])):
                            if a.get("id") == answer_id:
                                if answer_text:
                                    update_data["questions"][i]["answers"][j]["text"] = answer_text
                                if is_correct is not None:
                                    update_data["questions"][i]["answers"][j]["is_correct"] = is_correct
                                break
                        break
                
                # Include title and status from current quiz
                update_data["title"] = current_quiz.get("title", "")
                update_data["status"] = current_quiz.get("status", "draft")
            
            else:
                print("Invalid choice.")
                continue
                
            if not update_data:
                print("No changes provided. Quiz will not be updated.")
                continue
                
            print("\nUpdating quiz...")
            print(f"Sending update data: {json.dumps(update_data, indent=2)}")
            result = await client.edit_quiz(quiz_id, update_data)
            print("\n--- Updated Quiz ---")
            print(json.dumps(result, indent=2))
            
        elif choice == "6":
            print("\n--- Delete Quiz ---")
            try:
                quiz_id = int(input("Enter quiz ID to delete: "))
            except ValueError:
                print("Invalid quiz ID.")
                continue
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete quiz {quiz_id}? (yes/no): ").strip().lower()
            if confirm not in ["yes", "y"]:
                print("Deletion cancelled.")
                continue
            
            result = await client.delete_quiz(quiz_id)
            if "error" in result:
                print(f"Failed to delete quiz: {result['error']}")
            else:
                print(f"Quiz {quiz_id} deleted successfully.")
        
        elif choice == "0":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main()) 