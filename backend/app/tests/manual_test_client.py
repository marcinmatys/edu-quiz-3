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
        
        elif choice == "0":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main()) 