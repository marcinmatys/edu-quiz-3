Jesteś doświadczonym architektem oprogramowania, którego zadaniem jest stworzenie szczegółowego planu wdrożenia punktu końcowego REST API. Twój plan poprowadzi zespół programistów w skutecznym i poprawnym wdrożeniu tego punktu końcowego.

Zanim zaczniemy, zapoznaj się z poniższymi informacjami:

1. Route API specification:
<route_api_specification>
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

</route_api_specification>


2. Database resources:
<db_resources>

Tables

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

</db_resources>

3. Definicje typów:
<type_definitions>
@schemas
</type_definitions>

4. Tech stack:
<tech_stack>
@tech-stack.md 
</tech_stack>

5. Implementation rules:
<implementation_rules>
@shared.mdc, @backend.mdc
</implementation_rules>

Twoim zadaniem jest stworzenie kompleksowego planu wdrożenia endpointu interfejsu API REST. Przed dostarczeniem ostatecznego planu użyj znaczników <analysis>, aby przeanalizować informacje i nakreślić swoje podejście. W tej analizie upewnij się, że:

1. Podsumuj kluczowe punkty specyfikacji API.
2. Wymień wymagane i opcjonalne parametry ze specyfikacji API.
3. Wymień niezbędne typy DTO (Pydantic schemas).
4. Zastanów się, jak wyodrębnić logikę do service (istniejącego lub nowego, jeśli nie istnieje).
5. Zaplanuj walidację danych wejściowych zgodnie ze specyfikacją API endpointa, zasobami bazy danych i regułami implementacji.
6. Określenie sposobu rejestrowania błędów w tabeli błędów (jeśli dotyczy).
7. Identyfikacja potencjalnych zagrożeń bezpieczeństwa w oparciu o specyfikację API i stack technologiczny.
8. Nakreśl potencjalne scenariusze błędów i odpowiadające im kody stanu.

Po przeprowadzeniu analizy utwórz szczegółowy plan wdrożenia w formacie markdown. Plan powinien zawierać następujące sekcje:

1. Przegląd punktu końcowego
2. Szczegóły żądania
3. Szczegóły odpowiedzi
4. Przepływ danych
5. Względy bezpieczeństwa
6. Obsługa błędów
7. Wydajność
8. Kroki implementacji

W całym planie upewnij się, że
- Używać prawidłowych kodów stanu API:
  - 200 dla pomyślnego odczytu
  - 201 dla pomyślnego utworzenia
  - 400 dla nieprawidłowych danych wejściowych
  - 401 dla nieautoryzowanego dostępu
  - 404 dla nie znalezionych zasobów
  - 500 dla błędów po stronie serwera
- Dostosowanie do dostarczonego stacku technologicznego
- Postępuj zgodnie z podanymi zasadami implementacji

Końcowym wynikiem powinien być dobrze zorganizowany plan wdrożenia w formacie markdown. Oto przykład tego, jak powinny wyglądać dane wyjściowe:

``markdown
# API Endpoint Implementation Plan: [Nazwa punktu końcowego]

## 1. Przegląd punktu końcowego
[Krótki opis celu i funkcjonalności punktu końcowego]

## 2. Szczegóły żądania
- Metoda HTTP: [GET/POST/PUT/DELETE]
- Struktura URL: [wzorzec URL]
- Parametry:
  - Wymagane: [Lista wymaganych parametrów]
  - Opcjonalne: [Lista opcjonalnych parametrów]
- Request Body: [Struktura treści żądania, jeśli dotyczy]

## 3. Wykorzystywane typy
[DTOs (Pydantic schemas) niezbędne do implementacji]

## 3. Szczegóły odpowiedzi
[Oczekiwana struktura odpowiedzi i kody statusu]

## 4. Przepływ danych
[Opis przepływu danych, w tym interakcji z zewnętrznymi usługami lub bazami danych]

## 5. Względy bezpieczeństwa
[Szczegóły uwierzytelniania, autoryzacji i walidacji danych]

## 6. Obsługa błędów
[Lista potencjalnych błędów i sposób ich obsługi]

## 7. Rozważania dotyczące wydajności
[Potencjalne wąskie gardła i strategie optymalizacji]

## 8. Etapy wdrożenia
1. [Krok 1]
2. [Krok 2]
3. [Krok 3]
...
```

Końcowe wyniki powinny składać się wyłącznie z planu wdrożenia w formacie markdown i nie powinny powielać ani powtarzać żadnej pracy wykonanej w sekcji analizy.

Pamiętaj, aby zapisać swój plan wdrożenia jako doc/endpoint-quizzes-result-plan.md. Upewnij się, że plan jest szczegółowy, przejrzysty i zapewnia kompleksowe wskazówki dla zespołu programistów.