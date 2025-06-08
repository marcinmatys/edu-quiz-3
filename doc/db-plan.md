# Database Schema for EDU-QUIZ

This document outlines the complete database schema for the EDU-QUIZ application, designed for use with SQLite.

## 1. Tables

### `users`
Stores user account information.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the user. |
| `username` | TEXT(64) | NOT NULL, UNIQUE | User's unique username. |
| `hashed_password` | TEXT | NOT NULL | Hashed password for the user. |
| `role` | TEXT | NOT NULL | User's role ('admin' or 'student'). |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of user creation. |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last user update. |

### `levels`
Stores predefined difficulty levels for quizzes.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the level. |
| `code` | TEXT | NOT NULL, UNIQUE | Short code for the level (e.g., 'I', 'II', 'VIII'). |
| `description` | TEXT | NOT NULL | Full description of the level (e.g., 'Klasa I', 'Klasa II'). |
| `level` | INTEGER | NOT NULL, UNIQUE | Numeric representation of the level for sorting. |

### `quizzes`
Stores quiz information.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the quiz. |
| `title` | TEXT(256) | NOT NULL | The title or subject of the quiz. |
| `status` | TEXT | NOT NULL | The status of the quiz ('draft' or 'published'). |
| `level_id` | INTEGER | NOT NULL, FOREIGN KEY (`levels.id`) | The difficulty level of the quiz. |
| `creator_id` | INTEGER | NOT NULL, FOREIGN KEY (`users.id`) | The user who created the quiz. |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of quiz creation. |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last quiz update. |

### `questions`
Stores the questions for each quiz.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the question. |
| `text` | TEXT(512) | NOT NULL | The text of the question. |
| `quiz_id` | INTEGER | NOT NULL, FOREIGN KEY (`quizzes.id`, ON DELETE CASCADE) | The quiz this question belongs to. |

### `answers`
Stores the possible answers for each question.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the answer. |
| `text` | TEXT(128) | NOT NULL | The text of the answer. |
| `is_correct` | INTEGER | NOT NULL, CHECK (`is_correct` IN (0, 1)) | Indicates if the answer is correct (1) or not (0). |
| `question_id` | INTEGER | NOT NULL, FOREIGN KEY (`questions.id`, ON DELETE CASCADE) | The question this answer belongs to. |

### `results`
Stores the results of quizzes taken by users.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the result entry. |
| `score` | INTEGER | NOT NULL | The number of correct answers. |
| `max_score` | INTEGER | NOT NULL | The total number of questions in the quiz. |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY (`users.id`, ON DELETE CASCADE) | The user who took the quiz. |
| `quiz_id` | INTEGER | NOT NULL, FOREIGN KEY (`quizzes.id`, ON DELETE CASCADE) | The quiz that was taken. |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of when the quiz was completed. |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of when the result was last updated. |
| | | UNIQUE (`user_id`, `quiz_id`) | Ensures only the last score for a user's quiz is stored. |

## 2. Relationships

- **`users` to `quizzes`**: One-to-Many. One user (admin) can create many quizzes. (`quizzes.creator_id` -> `users.id`)
- **`levels` to `quizzes`**: One-to-Many. One level can be assigned to many quizzes. (`quizzes.level_id` -> `levels.id`)
- **`quizzes` to `questions`**: One-to-Many. One quiz consists of many questions. (`questions.quiz_id` -> `quizzes.id`)
- **`questions` to `answers`**: One-to-Many. One question has many answers (typically 4). (`answers.question_id` -> `questions.id`)
- **`users` to `results`**: One-to-Many. One user can have results for many different quizzes. (`results.user_id` -> `users.id`)
- **`quizzes` to `results`**: One-to-Many. One quiz can be taken by many users. (`results.quiz_id` -> `quizzes.id`)

## 3. Indexes

To optimize query performance, the following indexes should be created:

- `idx_quizzes_status`: On `quizzes(status)` for efficient filtering of quizzes by their status.
- `idx_quizzes_level_id`: On `quizzes(level_id)` for efficient sorting and filtering by level.
- `idx_questions_quiz_id`: On `questions(quiz_id)`. (Implicitly created for the foreign key in many systems, but explicit is better).
- `idx_answers_question_id`: On `answers(question_id)`. (Implicitly created for the foreign key).
- `idx_results_user_id`: On `results(user_id)`. (Implicitly created for the foreign key).
- `idx_results_quiz_id`: On `results(quiz_id)`. (Implicitly created for the foreign key).
- The `UNIQUE` constraint on `results(user_id, quiz_id)` also creates an index automatically.

## 4. SQLite Rules

- **Foreign Key Support**: Foreign key constraints must be enabled at runtime for each connection using the command `PRAGMA foreign_keys = ON;`. SQLAlchemy handles this automatically.
- **Triggers for `updated_at`**: To automatically update the `updated_at` timestamp on row changes, triggers are required.

  ```sql
  CREATE TRIGGER update_users_updated_at
  AFTER UPDATE ON users
  FOR EACH ROW
  BEGIN
      UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
  END;
  ```
  *(Similar triggers should be created for `quizzes` and `results` tables).*

## 5. Design Notes

- **Normalization**: The schema is designed in 3rd Normal Form (3NF).
- **Business Logic**: Complex rules, such as preventing the editing of a published quiz that has been attempted by a student, will be handled in the application layer (FastAPI), not at the database level.
- **Data Seeding**: The `levels` table and initial `users` (one admin, one student) will be pre-populated via a data seeding script during application setup.
- **Boolean Representation**: The `answers.is_correct` column uses an `INTEGER` type with a `CHECK` constraint (`0` for false, `1` for true) for compatibility.
- **Cascade Deletion**: `ON DELETE CASCADE` is used to maintain referential integrity. For instance, deleting a quiz will automatically remove all its associated questions, answers, and results, simplifying data management. 