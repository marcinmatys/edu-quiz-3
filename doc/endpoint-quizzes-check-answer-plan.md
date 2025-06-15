# API Endpoint Implementation Plan: POST /quizzes/{quiz_id}/check-answer

## 1. Przegląd punktu końcowego
Ten punkt końcowy umożliwia uwierzytelnionemu studentowi sprawdzenie pojedynczej odpowiedzi na pytanie w ramach określonego quizu. W odpowiedzi serwer zwraca informację o poprawności odpowiedzi, identyfikator poprawnej opcji oraz wyjaśnienie wygenerowane przez AI. Operacja ma charakter "tylko do odczytu" i nie modyfikuje stanu bazy danych.

## 2. Szczegóły żądania
- **Metoda HTTP**: `POST`
- **Struktura URL**: `/quizzes/{quiz_id}/check-answer`
- **Parametry**:
  - **Wymagane**:
    - `quiz_id` (w ścieżce): Identyfikator (INTEGER) quizu.
- **Request Body**: Ciało żądania musi być w formacie `application/json` i zawierać następujące pola:
  ```json
  {
    "question_id": 1,
    "answer_id": 2
  }
  ```
  - `question_id` (wymagane): Identyfikator (INTEGER) pytania.
  - `answer_id` (wymagane): Identyfikator (INTEGER) odpowiedzi wybranej przez studenta.

## 3. Wykorzystywane typy
Do implementacji zostaną wykorzystane następujące schematy Pydantic z modułu `backend/app/schemas/`:
- **Żądanie**: `schemas.AnswerCheck`
- **Odpowiedź**: `schemas.AnswerCheckResponse`

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu (Success Response)**: `200 OK`
  - Zwraca obiekt JSON zgodny ze schematem `AnswerCheckResponse`.
  ```json
  {
    "is_correct": true,
    "correct_answer_id": 2,
    "explanation": "Wyjaśnienie wygenerowane przez AI..."
  }
  ```
- **Odpowiedzi błędów (Error Responses)**: Zobacz sekcję 6. Obsługa błędów.

## 5. Przepływ danych
1.  Żądanie `POST` trafia do routera FastAPI.
2.  FastAPI automatycznie waliduje typ `quiz_id` (int) oraz ciało żądania względem schematu `AnswerCheck`.
3.  Uruchamiana jest zależność (dependency) bezpieczeństwa, która weryfikuje token JWT, sprawdza, czy użytkownik jest aktywny i posiada rolę `student`.
4.  Router wywołuje funkcję serwisową, np. `quiz_service.check_answer(db, quiz_id, answer_check_data, current_user)`.
5.  Serwis wykonuje następujące operacje:
    a. Pobiera z bazy danych quiz o podanym `quiz_id`. Sprawdza, czy quiz istnieje i ma status `published`. Jeśli nie, zwraca błąd `404 Not Found`.
    b. Pobiera z bazy pytanie o `question_id` i sprawdza, czy jest ono powiązane z pobranym quizem. Jeśli nie, zwraca błąd `404 Not Found`.
    c. Pobiera z bazy wybraną przez studenta odpowiedź (`answer_id`) oraz wszystkie pozostałe odpowiedzi dla danego pytania. Sprawdza, czy wybrana odpowiedź należy do pytania. Jeśli nie, zwraca błąd `404 Not Found`.
    d. Ustala, czy wybrana odpowiedź jest poprawna (`is_correct`) i identyfikuje ID poprawnej odpowiedzi.
    e. Wywołuje serwis AI (np. `ai_service.generate_explanation()`), przekazując tekst pytania i tekst poprawnej odpowiedzi, aby uzyskać wyjaśnienie.
    f. Konstruuje obiekt DTO `AnswerCheckResponse` z uzyskanymi danymi.
6.  Router odbiera DTO od serwisu i zwraca klientowi odpowiedź `200 OK` z serializowanym obiektem.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Endpoint musi być chroniony. Dostęp jest przyznawany wyłącznie na podstawie ważnego tokenu JWT.
- **Autoryzacja**: Zależność (dependency) musi weryfikować, czy rola użytkownika w tokenie to `student`. Użytkownicy z rolą `admin` nie powinni mieć dostępu.
- **Walidacja danych**:
  - Wszystkie dane wejściowe (`quiz_id`, `question_id`, `answer_id`) muszą być rygorystycznie walidowane, aby upewnić się, że student operuje wyłącznie w kontekście zasobów, do których ma prawo (tj. pytanie musi należeć do quizu, a odpowiedź do pytania). Zapobiega to próbom odpytywania o niepowiązane dane.
  - Quiz musi mieć status `published`.

## 7. Obsługa błędów
Należy zaimplementować spójną obsługę błędów z odpowiednimi kodami stanu HTTP:
- **`401 Unauthorized`**: Token JWT jest nieprawidłowy, wygasł lub nie został dostarczony.
- **`403 Forbidden`**: Użytkownik jest uwierzytelniony, ale nie ma roli `student`.
- **`404 Not Found`**:
  - Nie znaleziono quizu o podanym `quiz_id` lub nie ma on statusu `published`.
  - Nie znaleziono pytania o podanym `question_id` w ramach danego quizu.
  - Nie znaleziono odpowiedzi o podanym `answer_id` w ramach danego pytania.
- **`422 Unprocessable Entity`**: Ciało żądania jest nieprawidłowe (np. brakuje pól, zły typ danych). Obsługiwane automatycznie przez FastAPI.
- **`500 Internal Server Error`**: Wystąpił błąd po stronie serwera, np. błąd połączenia z bazą danych lub błąd podczas komunikacji z zewnętrznym serwisem AI. Należy zalogować szczegóły błędu.

## 8. Rozważania dotyczące wydajności
- Główne potencjalne wąskie gardło to czas odpowiedzi zewnętrznego serwisu AI generującego wyjaśnienie.
- Należy rozważyć zaimplementowanie `timeout` dla zapytania do serwisu AI, aby uniknąć długiego oczekiwania klienta w przypadku problemów z usługą.
- Zapytania do bazy danych powinny być zoptymalizowane i korzystać z indeksów na kluczach obcych (`quiz_id`, `question_id`).

## 9. Etapy wdrożenia
1.  **Router**: W pliku `backend/app/routers/quiz.py` dodać nową operację ścieżki dla `POST /quizzes/{quiz_id}/check-answer`.
2.  **Bezpieczeństwo**: Zaimplementować i dołączyć zależność (dependency), która weryfikuje uwierzytelnienie i rolę `student`.
3.  **Serwis AI**: Jeśli nie istnieje, stworzyć nowy moduł `backend/app/services/ai_service.py` z funkcją `generate_explanation(question_text: str, correct_answer_text: str) -> str`, która będzie komunikować się z API OpenAI.
4.  **Serwis Quizu**: W module `backend/app/services/quiz_service.py` (lub podobnym) zaimplementować główną logikę w funkcji `check_answer(...)`.
5.  **CRUD**: Wykorzystać istniejące funkcje CRUD (`crud.quiz.get`, `crud.question.get`, `crud.answer.get`) do pobierania danych z bazy. Upewnić się, że funkcje te pozwalają na efektywne filtrowanie i weryfikację przynależności (np. `crud.question.get_by_quiz_id`).
6.  **Integracja**: Połączyć logikę w routerze, wywołując serwis i obsługując zwracane przez niego dane lub wyjątki.
7.  **Testy**: Stworzyć testy jednostkowe dla logiki w serwisie, obejmujące przypadki sukcesu i wszystkie scenariusze błędów.
8.  **Testy integracyjne**: Dodać testy dla całego endpointu, symulując żądania HTTP i weryfikując odpowiedzi, w tym kody statusu i strukturę danych. Należy zamockować wywołanie serwisu AI.
9.  **Dokumentacja**: Upewnić się, że endpoint jest poprawnie udokumentowany w generowanej automatycznie dokumentacji Swagger/OpenAPI. 