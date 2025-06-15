# EDU-QUIZ

[![Project Status: In Development](https://img.shields.io/badge/status-in_development-blue.svg)](https://github.com/your-repo/edu-quiz)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An educational application for creating and conducting interactive, AI-powered quizzes.

## Table of Contents
1. [Project Description](#project-description)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Getting Started Locally](#getting-started-locally)
5. [User Interface](#user-interface)
6. [Project Scope](#project-scope)
7. [Project Status](#project-status)
8. [Development Information/Statistics](#development-informationstatistics)
11. [License](#license)

## Project Description

EDU-QUIZ is an educational application designed for creating and conducting interactive quizzes at the school level. The system utilizes Artificial Intelligence (AI) to generate quiz content, aiming to simplify the workload for teachers and enhance student engagement.

The application addresses two main user problems:
-   **For the administrator (teacher):** It automates the time-consuming process of creating diverse and engaging quizzes, maintaining high-quality educational content.
-   **For the student:** It provides an interactive and engaging learning format with immediate feedback, motivating further learning through gamification elements.

The system distinguishes between two user roles: an **administrator**, who manages quizzes and accounts, and a **student**, who browses, launches, and completes quizzes, receiving instant feedback.

## Tech Stack

### Frontend
-   **React 19:** A popular framework for building dynamic and responsive user interfaces.
-   **Tailwind 4:** A utility-first CSS framework for convenient application styling.
-   **Shadcn/ui:** A component library providing accessible React components.

### Backend
-   **Python & FastAPI:** A modern, fast web framework for building APIs.
-   **Uvicorn:** An ASGI server for running the FastAPI application.
-   **OpenAI API:** For communication with LLM models to generate quiz content.

### Database
-   **SQLAlchemy:** An ORM for database management.
-   **SQLite:** The database engine used for the project.

### Authentication
-   **JWT (JSON Web Tokens):** Used for securing user authentication and session management, integrated within FastAPI.

### CI/CD & Hosting
-   **GitHub Actions:** For creating CI/CD pipelines.
-   **DigitalOcean:** For hosting the application via Docker images.

## Project Structure

This project is split into two main parts:
- **frontend/**: React 19 + Vite + Tailwind + Shadcn/ui (student/admin UI)
- **backend/**: Python FastAPI + SQLite (API server)

The backend is organized for future scalability, with distinct modules for routers, models, schemas, database connections, and core configuration.

For more detailed information about the backend structure, API endpoints, testing procedures, and rate limiting configuration, see the [Backend README](backend/README.md).

For comprehensive database management options, including GUI tools, command-line interfaces, debug endpoints, and programmatic access via SQLAlchemy, refer to the [Database Documentation](backend/README-db.md).

## Getting Started Locally

To set up and run the project on your local machine, follow these steps.

### Prerequisites
-   Node.js and npm
-   Python 3.8+ and pip
-   Git

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-repo/edu-quiz.git
    cd edu-quiz
    ```

2.  **Set up the Backend:**
    ```sh
    # Navigate to the backend directory
    cd backend

    # Create a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install dependencies
    pip install -r requirements.txt

    # Create a .env file and add your OpenAI API key
    # OPENAI_API_KEY="your_api_key_here"

    # Run the development server
    uvicorn app.main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`. You can test it by accessing the `http://127.0.0.1:8000/ping` endpoint.

3.  **Set up the Frontend:**
    ```sh
    # Navigate to the frontend directory
    cd frontend

    # Install dependencies
    npm install

    # Run the development server
    npm run dev
    ```
    The frontend will be running at `http://localhost:5173`.

## Default user accounts

On startup, the application automatically:
- Creates all database tables if they don't exist
- Seeds the database with:
  - Predefined difficulty levels (Classes I-VIII)
  - Default admin user
  - Default student user

You can use the following credentials to log in and test the application:

-   **Admin User:**
    -   **Username:** `admin`
    -   **Password:** `admin123`
-   **Student User:**
    -   **Username:** `student`
    -   **Password:** `student123`

## User Interface

Below are screenshots of the key interfaces in the application:

### Authentication

![Login Screen](doc/ui/login.png)  
*Login screen where users can authenticate as either an administrator or a student.*

### Administrator Interface

![Admin Dashboard](doc/ui/admin-dashboard.png)
*Administrator dashboard giving access to various features, including quiz management.*

![Admin Quizzes](doc/ui/admin-quizzes.png)
*Administrator quiz management screen displaying all quizzes, with options to create, edit, delete, and status for each quiz.*

![Create New Quiz](doc/ui/new-quizz.png)  
*Interface for creating a new quiz with AI assistance, allowing specification of topic, difficulty level, and number of questions.*

![Edit Quiz](doc/ui/edit-quizz.png)
*Quiz editing interface where administrators can modify title, questions, answers, and publish/unpublish the quiz.*

### Student Interface

![Student Dashboard](doc/ui/student-dashboard.png)
*Student dashboard providing access to various features, including browsing and taking quizzes.*

![Student Quizzes](doc/ui/student-quizzes.png)
*List of available quizzes for students, displaying quiz title, difficulty level, and previous scores if applicable.*

![Quiz Question](doc/ui/student-question.png)
*Quiz interface that allows students to answer questions, displays progress, and shows an AI-generated explanation after submitting an answer.*

![Quiz Summary](doc/ui/quizz-summary.png)
*Summary screen displayed after completing a quiz, showing the final score.*

## Project Scope

### Key Features (MVP)

The MVP (Minimum Viable Product) delivers the core features for a complete quiz lifecycle: AI-powered creation, administrator management, and a dynamic and engaging learning experience for students.

**Administrator Features:**
-   **AI-Powered Quiz Generation:** Quickly create quizzes by specifying a topic, number of questions, and difficulty level (corresponding to school grades 1-8). The AI generates questions and four multiple-choice answer options.
-   **Full Quiz Lifecycle Management:** A dedicated admin panel provides complete control over quizzes, including:
    -   **Creation:** Generate new quizzes with AI assistance.
    -   **Review & Edit:** Manually review and modify AI-generated content (questions, answers) to ensure quality.
    -   **Publishing:** Publish quizzes to make them available for students, or unpublish them.
    -   **Deletion:** Remove quizzes from the system.

**Student Features:**
-   **Quiz Library:** Browse a list of all published quizzes, sorted by difficulty level.
-   **Taking Quizzes:** A simple and interactive interface for taking quizzes one question at a time.
-   **Instant Feedback:** Receive immediate feedback after each answer. The system indicates if the answer was correct or incorrect and provides a brief, AI-generated explanation to aid learning.
-   **Results Summary:** Upon completing a quiz, view a summary screen with the final score (e.g., 7/10).
-   **Score Persistence:** The most recent score for each completed quiz is saved and displayed next to the quiz in the student's list, allowing them to track their performance.

### Future Enhancements

To keep the MVP focused, the following features are planned for future releases:

-   **Full User Management:** Moving beyond the initial static accounts to allow for user registration, profile management, and distinct accounts for multiple students and admins.
-   **Advanced Admin Analytics:** A comprehensive dashboard for administrators to view detailed statistics on student performance and quiz effectiveness.
-   **Timed Quizzes:** The ability to set time limits for quizzes to add a layer of challenge.
-   **Quiz Progression:** Allowing students to save their progress and resume interrupted quizzes at a later time.
-   **Expanded Question Formats:** Introducing a variety of question types, such as multi-select, fill-in-the-blank, and open-ended questions.
-   **Gamification Elements:** Implementing features like badges, points, and leaderboards to further motivate students.
-   **Multimedia in Quizzes:** Adding support for including images or short video clips in questions and answers.
-   **Deeper Learning Analytics:** Providing students with insights into their performance, highlighting strengths and areas needing improvement based on quiz results.

## Project Status
This project is currently in the **MVP phase**. Core minimum features are being built and tested.

## Development Information/Statistics

-   **Tools used:** Cursor
-   **Models used:** **gemini-2.5-pro**, **claude-3.7-sonet**, o3-mini, gpt-4.1
-   **Work time:** Approximately one week
-   **Number of files in the project:** 185
-   **Number of lines of code/documentation in the project:** 24,745
-   **Percentage of generated (by AI) code/documentation:** I'd say around 98%
-   **Development Approach and Notes** – The MVP concept for the project was initially written manually. This was followed by fully supervised planning of individual tasks and implementation in collaboration with Cursor. The project was created as part of completing the [10xDevs training program](https://www.10xdevs.pl/). Throughout its development, I relied heavily on the knowledge, work techniques, and prompts provided during the course. However, the project was built using my own technology stack, with the frontend technologies partially overlapping with those recommended in the training.
-   **Code Quality Disclaimer** – While the code quality may not be optimal in all areas, the project was developed under tight time constraints for educational purposes and as part of the 10xDevs training completion. The main goal was to demonstrate how, with the right techniques and tools like Cursor, it's possible to rapidly deliver a functional MVP version of an application.


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
