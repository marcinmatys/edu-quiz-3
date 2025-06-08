# REST API Plan

This document outlines the REST API for the EDU-QUIZ application, designed based on the project's PRD and database schema.

## 1. Resources

- **Auth**: Handles user authentication.
- **Users**: Represents user accounts. (Limited to fetching current user info as per PRD).
- **Levels**: Represents difficulty levels for quizzes.
- **Quizzes**: The core resource, representing the quizzes. Includes questions and answers.
- **Results**: Represents the results of quizzes taken by students.

## 2. Endpoints

---

### **Auth**

#### POST /token

- **Description**: Authenticates a user and returns a JWT access token.
- **Request Body**: `application/x-www-form-urlencoded`
  - `username` (string, required)
  - `password` (string, required)
- **Success Response**: `200 OK`
  ```json
  {
    "access_token": "your.jwt.token",
    "token_type": "bearer"
  }
  ```
- **Error Response**: `401 Unauthorized`
  ```json
  {
    "detail": "Incorrect username or password"
  }
  ```

---

### **Users**

#### GET /users/me

- **Description**: Retrieves the profile of the currently authenticated user.
- **Authentication**: Required.
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2023-10-27T10:00:00Z"
  }
  ```
- **Error Response**: `401 Unauthorized`

---

### **Levels**

#### GET /levels

- **Description**: Retrieves a list of all available difficulty levels.
- **Authentication**: Required.
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "code": "I",
      "description": "Klasa I",
      "level": 1
    },
    {
      "id": 2,
      "code": "II",
      "description": "Klasa II",
      "level": 2
    }
  ]
  ```
- **Error Response**: `401 Unauthorized`

---

### **Quizzes**

#### GET /quizzes

- **Description**: Retrieves a list of quizzes. Admins see all quizzes; students see only 'published' ones.
- **Authentication**: Required.
- **Query Parameters**:
  - `sort_by` (string, optional, e.g., 'level'): Field to sort by. Defaults to `level`.
  - `order` (string, optional, 'asc' or 'desc'): Sort order. Defaults to `asc`.
  - `status` (string, optional, 'draft' or 'published'): Filters by status. (Admin only).
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "title": "Historia Polski",
      "status": "published",
      "level_id": 5,
      "creator_id": 1,
      "question_count": 10,
      "last_result": { // Present only for students who have a result
        "score": 8,
        "max_score": 10
      },
      "updated_at": "2023-10-27T12:00:00Z"
    }
  ]
  ```
- **Error Response**: `401 Unauthorized`

#### POST /quizzes/generate

- **Description**: Generates a new quiz using AI and saves it as a 'draft'.
- **Authentication**: Required (Admin only).
- **Request Body**:
  ```json
  {
    "topic": "Historia Polski",
    "question_count": 10,
    "level_id": 5
  }
  ```
- **Success Response**: `201 Created`
  - The response body contains the newly generated quiz object, including all questions and answers, for immediate review.
  ```json
  {
    "id": 2,
    "title": "Historia Polski",
    "status": "draft",
    "level_id": 5,
    "creator_id": 1,
    "questions": [
      {
        "id": 3,
        "text": "Kto był pierwszym królem Polski?",
        "answers": [
          {"id": 10, "text": "Mieszko I", "is_correct": false},
          {"id": 11, "text": "Bolesław Chrobry", "is_correct": true},
          // ... other answers
        ]
      }
      // ... other questions
    ]
  }
  ```
- **Error Response**: `422 Unprocessable Entity` (Validation error), `503 Service Unavailable` (AI service error).

#### GET /quizzes/{quiz_id}

- **Description**: Retrieves a specific quiz with all its questions and answers. For students, the `is_correct` field is omitted.
- **Authentication**: Required.
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "title": "Historia Polski",
    "status": "published",
    "questions": [
        {
            "id": 1,
            "text": "Kto był pierwszym królem Polski?",
            "answers": [
                {"id": 1, "text": "Mieszko I"},
                {"id": 2, "text": "Bolesław Chrobry"},
                {"id": 3, "text": "Kazimierz Wielki"},
                {"id": 4, "text": "Władysław Łokietek"}
            ]
        }
        // ... more questions
    ]
  }
  ```
  *Note: For admins, the `answers` array will include the `"is_correct": true/false` field.*
- **Error Response**: `404 Not Found`

#### PUT /quizzes/{quiz_id}

- **Description**: Updates a quiz. Used by admins to edit questions/answers and to change the status from 'draft' to 'published'.
- **Authentication**: Required (Admin only).
- **Request Body**:
  ```json
  {
    "title": "Nowy Tytuł Quizu",
    "status": "published", // Optional: change status
    "level_id": 4,
    "questions": [
      {
        "id": 1, // Include ID for existing questions
        "text": "Zaktualizowane pytanie?",
        "answers": [
          {"id": 1, "text": "Zmieniona odp A", "is_correct": false},
          {"id": 2, "text": "Zmieniona odp B", "is_correct": true}
          // ... other answers
        ]
      },
      {
        "text": "Nowe pytanie?", // No ID for new questions
        "answers": [
            // ... new answers
        ]
      }
    ]
  }
  ```
- **Success Response**: `200 OK` (with the updated quiz object in the body).
- **Error Response**: `404 Not Found`, `422 Unprocessable Entity`.

#### DELETE /quizzes/{quiz_id}

- **Description**: Deletes a quiz and all its associated questions, answers, and results (due to DB cascade).
- **Authentication**: Required (Admin only).
- **Success Response**: `204 No Content`
- **Error Response**: `404 Not Found`

#### POST /quizzes/{quiz_id}/check-answer

- **Description**: Checks a single answer for a student, providing immediate feedback and an AI-generated explanation without persisting data.
- **Authentication**: Required (Student only).
- **Request Body**:
  ```json
  {
    "question_id": 1,
    "answer_id": 2
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "is_correct": true,
    "correct_answer_id": 2,
    "explanation": "Bolesław Chrobry został koronowany w 1025 roku, co czyni go pierwszym królem Polski."
  }
  ```
- **Error Response**: `404 Not Found`, `422 Unprocessable Entity`.

---

### **Results**

#### POST /quizzes/{quiz_id}/results

- **Description**: Submits the final results of a completed quiz for a student. Creates or updates the result entry.
- **Authentication**: Required (Student only).
- **Request Body**:
  ```json
  {
    "score": 8,
    "max_score": 10
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": 5,
    "score": 8,
    "max_score": 10,
    "user_id": 2,
    "quiz_id": 1,
    "created_at": "2023-10-27T14:00:00Z"
  }
  ```
- **Error Response**: `404 Not Found`, `422 Unprocessable Entity`.

## 3. Authentication and Authorization

- **Mechanism**: Authentication will be handled using JSON Web Tokens (JWT).
- **Flow**:
  1. A user submits their credentials to `POST /token`.
  2. The server validates the credentials and, if successful, issues a short-lived JWT `access_token`.
  3. The client must include this token in the `Authorization` header for all subsequent protected requests (e.g., `Authorization: Bearer <token>`).
- **Authorization**:
  - API endpoints will be protected based on the user's role (`admin` or `student`), which is encoded in the JWT.
  - **Admin routes**: Quiz creation, generation, updating, and deletion.
  - **Student routes**: Listing published quizzes, taking quizzes, checking answers, and submitting results.
  - Shared routes like `GET /levels` are accessible to any authenticated user.

## 4. Validation and Business Logic

- **Validation**: All incoming request bodies (`POST`, `PUT`) will be validated against Pydantic schemas that mirror the constraints defined in the database schema (e.g., required fields, max length, data types). If validation fails, the API will return a `422 Unprocessable Entity` response with details about the error.
- **Business Logic**:
  - **AI Generation**: The `POST /quizzes/generate` endpoint encapsulates the logic of calling an external AI service, parsing its response, and structuring the data into the database format.
  - **Immediate Feedback**: The `POST /quizzes/{quiz_id}/check-answer` endpoint is a dedicated RPC-style endpoint to implement the immediate feedback feature securely.
  - **Status Flow**: The `status` field (`draft` -> `published`) of a quiz is managed via the `PUT /quizzes/{quiz_id}` endpoint. The API will ensure that only published quizzes are visible to students.
  - **Result Uniqueness**: The database constraint `UNIQUE (user_id, quiz_id)` on the `results` table is handled by the `POST /quizzes/{quiz_id}/results` endpoint, which will perform an "upsert" (update or insert) operation to store only the latest score for a user on a given quiz. 