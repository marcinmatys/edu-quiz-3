# API Endpoint Implementation Plan: POST /quizzes

## 1. Przegląd punktu końcowego
Ten punkt końcowy jest odpowiedzialny za generowanie nowego quizu przy użyciu zewnętrznej usługi AI. Otrzymuje temat, liczbę pytań i poziom trudności, a następnie tworzy kompletny quiz (wraz z pytaniami i odpowiedziami) i zapisuje go w systemie ze statusem 'draft'. Punkt końcowy jest dostępny tylko dla uwierzytelnionych użytkowników z rolą 'admin'.

## 2. Szczegóły żądania
- **Metoda HTTP**: `POST`
- **Struktura URL**: `/api/v1/quizzes`
- **Nagłówki**:
  - `Authorization`: `Bearer <JWT_TOKEN>` (Wymagane)
- **Request Body**:
  ```json
  {
    "topic": "string",
    "question_count": "integer",
    "level_id": "integer"
  }
  ```

## 3. Wykorzystywane typy
Będą wymagane następujące schematy Pydantic (do zdefiniowania w `backend/app/schemas/quiz.py` i powiązanych plikach):

- **`QuizCreateRequest`**: Schemat dla ciała żądania.
  - `topic: str`
  - `question_count: int` = Field(gt=0, le=20) - *Liczba pytań musi być dodatnia i nie większa niż 20.*
  - `level_id: int`

- **`AnswerResponse`**: Schemat dla pojedynczej odpowiedzi.
  - `id: int`
  - `text: str`
  - `is_correct: bool`

- **`QuestionResponse`**: Schemat dla pojedynczego pytania z zagnieżdżonymi odpowiedziami.
  - `id: int`
  - `text: str`
  - `answers: List[AnswerResponse]`

- **`QuizResponse`**: Główny schemat odpowiedzi, reprezentujący nowo utworzony quiz.
  - `id: int`
  - `title: str`
  - `status: str`
  - `level_id: int`
  - `creator_id: int`
  - `questions: List[QuestionResponse]`

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu (`201 Created`)**:
  - Zwraca nowo utworzony obiekt quizu, zgodny ze schematem `QuizResponse`.
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
          {"id": 11, "text": "Bolesław Chrobry", "is_correct": true}
        ]
      }
    ]
  }
  ```
- **Odpowiedzi błędów**:
  - `400 Bad Request`: Ciało żądania jest nieprawidłowym JSON-em.
  - `401 Unauthorized`: Użytkownik nie jest uwierzytelniony.
  - `403 Forbidden`: Użytkownik jest uwierzytelniony, ale nie ma roli 'admin'.
  - `422 Unprocessable Entity`: Błąd walidacji danych wejściowych (np. `level_id` nie istnieje, `question_count` poza zakresem).
  - `503 Service Unavailable`: Wystąpił błąd podczas komunikacji z usługą AI lub przetwarzania jej odpowiedzi.

## 5. Przepływ danych
1.  Żądanie `POST /quizzes` trafia do serwera FastAPI.
2.  Uruchamiana jest zależność security, która weryfikuje token JWT i sprawdza, czy rola użytkownika to 'admin'.
3.  Ciało żądania jest walidowane względem schematu `QuizCreateRequest`.
4.  Router wywołuje funkcję serwisową (np. `QuizGenerationService.create_quiz_with_ai`).
5.  Serwis konstruuje prompt dla modelu AI, zawierający temat, liczbę pytań i informacje o poziomie trudności.
6.  Serwis wysyła żądanie do modelu gpt-4.1 poprzez API do platformy openai wykorzystując openai SDK i oczekuje na odpowiedź.
7.  Serwis parsuje odpowiedź AI. Jeśli jest nieprawidłowa lub wystąpił błąd, zwraca `503 Service Unavailable`.
8.  Serwis rozpoczyna transakcję bazodanową.
9. W ramach transakcji, serwis:
    a. Zapisuje nowy rekord w tabeli `quizzes` ze statusem 'draft'.
    b. Iteruje po wygenerowanych pytaniach i zapisuje je w tabeli `questions`, powiązując z nowym quizem.
    c. Dla każdego pytania, iteruje po odpowiedziach i zapisuje je w tabeli `answers`.
10. Jeśli wszystkie operacje bazodanowe powiodą się, transakcja jest zatwierdzana (commit). W przeciwnym razie jest wycofywana (rollback).
11. Serwis zwraca nowo utworzony obiekt quizu (wraz z relacjami) do routera.
12. Router konwertuje obiekt na odpowiedź JSON i wysyła ją do klienta z kodem statusu `201 Created`.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie i Autoryzacja**: Punkt końcowy musi być chroniony przez zależność, która weryfikuje token JWT i uprawnienia administratora. Należy stworzyć dedykowaną zależność `get_current_active_admin`.
- **Walidacja danych wejściowych**: Należy ściśle walidować wszystkie dane wejściowe (`topic`, `question_count`, `level_id`) za pomocą Pydantic, aby zapobiec błędom i atakom.
- **Ochrona przed Prompt Injection**: `topic` podany przez użytkownika będzie częścią promptu AI. Należy zadbać o odpowiednią konstrukcję systemowego promptu, aby ograniczyć możliwość manipulacji modelem przez złośliwie spreparowany `topic`.
- **Ograniczenie zasobów (Rate Limiting)**: Aby zapobiec nadużyciom i eskalacji kosztów związanych z API AI, należy zaimplementować mechanizm rate limiting dla tego punktu końcowego.

## 7. Rozważania dotyczące wydajności
- **Czas odpowiedzi AI**: Głównym wąskim gardłem wydajnościowym będzie czas odpowiedzi zewnętrznej usługi AI. Zapytania mogą trwać kilka sekund.
- **Operacje na bazie danych**: Wszystkie operacje zapisu do bazy danych powinny być wykonane w ramach jednej transakcji, aby zapewnić spójność danych i zminimalizować liczbę zapytań.
- **Asynchroniczność**: Operacja generowania quizu jest długotrwała. Należy w pełni wykorzystać asynchroniczność `FastAPI` i `SQLAlchemy`, aby nie blokować serwera podczas oczekiwania na odpowiedź od AI.

## 8. Etapy wdrożenia
1.  **Utworzenie zależności autoryzacji**: W `backend/app/core/security.py` stworzyć nową zależność `get_current_active_admin`, która bazuje na istniejącej logice autentykacji i dodatkowo sprawdza, czy `user.role == 'admin'`.
2.  **Implementacja serwisu AI**: Stworzyć nowy plik `backend/app/services/ai_quiz_generator.py`. Zawrzeć w nim logikę do komunikacji z API OpenAI, w tym konstruowanie promptu i parsowanie odpowiedzi.
3.  **Implementacja głównego serwisu**: Stworzyć plik `backend/app/services/quiz_service.py` (jeśli nie istnieje). Dodać metodę `create_ai_quiz`, która będzie orkiestrować cały proces: wywołanie serwisu AI, oraz zapis do bazy danych w ramach jednej transakcji.
4.  **Dodanie logiki CRUD**: Upewnić się, że istnieją odpowiednie funkcje CRUD do zapisu quizów, pytań i odpowiedzi w `backend/app/crud/`.
5.  **Implementacja routera**: W `backend/app/routers/quizzes.py` dodać nowy punkt końcowy `POST /`. Wstrzyknąć do niego zależność `get_current_active_admin` oraz `quiz_service`.
6.  **Obsługa błędów**: Zaimplementować obsługę wyjątków na poziomie serwisu i routera, zwracając odpowiednie kody statusu HTTP (`422`, `503`). Dodać szczegółowe logowanie błędów z serwisu AI.
7.  **Testy**: Napisać testy jednostkowe dla logiki serwisów oraz testy integracyjne dla nowego punktu końcowego, uwzględniając przypadki sukcesu i błędów. 