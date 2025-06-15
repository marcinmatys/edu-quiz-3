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
    a. Wywołuje metodę `get_quiz_by_id(db, quiz_id)` z `QuizService`, która pobiera z bazy danych pełny obiekt quizu wraz z listą pytań i ich odpowiedziami.
    b. Sprawdza, czy pobrany quiz istnieje i ma status `published`. Jeśli nie, zwraca błąd `404 Not Found`.
    c. Wyszukuje w pamięci (na pobranym obiekcie) pytanie o zadanym `question_id`. Jeśli pytanie nie należy do tego quizu, zwraca błąd `404 Not Found`.
    d. Wyszukuje w pamięci (w ramach znalezionego pytania) odpowiedź o zadanym `answer_id`. Jeśli odpowiedź nie należy do tego pytania, zwraca błąd `404 Not Found`.
    e. Ustala, czy wybrana odpowiedź jest poprawna (`is_correct`) i identyfikuje ID oraz treść poprawnej odpowiedzi.
    f. Wywołuje serwis AI (`ai_service.generate_explanation(...)`) w celu uzyskania wyjaśnienia. Proces ten obejmuje:
        i. Przygotowanie danych wejściowych: tytuł i poziom zaawansowania quizu, treść pytania, treść poprawnej odpowiedzi oraz (jeśli udzielono błędnej) treść odpowiedzi studenta.
        ii. Skonstruowanie precyzyjnego promptu dla modelu językowego (LLM), zlecającego wygenerowanie zwięzłego (do kilku zdań) wyjaśnienia, które tłumaczy, dlaczego odpowiedź jest poprawna i ewentualnie odnosi się do błędu studenta.
        iii. Wysłanie zapytania do API (np. OpenAI) i odebranie odpowiedzi.
    g. Konstruuje obiekt DTO `AnswerCheckResponse` z uzyskanymi danymi (włączając wyjaśnienie od AI).
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
- **`500 Internal Server Error`**: Wystąpił błąd po stronie serwera, np. błąd połączenia z bazą danych lub błąd podczas komunikacji z zewnętrznym serwisem AI. Należy zalogować szczegóły błędu. Należy również obsłużyć przypadki, gdy odpowiedź z serwisu AI jest pusta lub niepoprawna.

## 8. Rozważania dotyczące wydajności
- Główne potencjalne wąskie gardło to czas odpowiedzi zewnętrznego serwisu AI generującego wyjaśnienie.
- Złożoność promptu i ilość danych przesyłanych do serwisu AI może wpłynąć na czas odpowiedzi. Prompt powinien być zwięzły, ale kompletny.
- Należy rozważyć zaimplementowanie `timeout` dla zapytania do serwisu AI, aby uniknąć długiego oczekiwania klienta w przypadku problemów z usługą.
- Zamiast wykonywać wiele oddzielnych zapytań do bazy danych, `get_quiz_by_id` powinien za jednym razem pobrać cały graf obiektu (quiz z pytaniami i odpowiedziami), np. przy użyciu `selectinload` w SQLAlchemy. Może to zmniejszyć opóźnienie związane z komunikacją z bazą danych.

## 9. Etapy wdrożenia
1.  **Router**: W pliku `backend/app/routers/quiz.py` dodać nową operację ścieżki dla `POST /quizzes/{quiz_id}/check-answer`.
2.  **Bezpieczeństwo**: Zaimplementować i dołączyć zależność (dependency), która weryfikuje uwierzytelnienie i rolę `student`.
3.  **Serwis AI**: Stworzyć lub zaktualizować moduł `backend/app/services/ai_service.py`. Zaimplementować w nim funkcję `generate_explanation`, która będzie przyjmować dane kontekstowe (tytuł quizu, poziom), treść pytania, treść poprawnej odpowiedzi oraz opcjonalnie błędną odpowiedź studenta. Funkcja będzie odpowiedzialna za budowę promptu, komunikację z API OpenAI i zapewnienie, że wygenerowane wyjaśnienie jest zwięzłe.
4.  **Serwis Quizu**: W module `backend/app/services/quiz_service.py` (lub podobnym) zaimplementować główną logikę w funkcji `check_answer(...)`.
5.  **Serwis/CRUD**: Zaimplementować lub wykorzystać istniejącą metodę `quiz_service.get_quiz_by_id(db, quiz_id)`, która efektywnie pobiera cały obiekt quizu, włączając w to pytania i odpowiedzi (np. z użyciem `selectinload` w warstwie CRUD).
6.  **Integracja**: Połączyć logikę w routerze, wywołując serwis i obsługując zwracane przez niego dane lub wyjątki.
7.  **Testy**: Stworzyć testy jednostkowe dla logiki w serwisie, obejmujące przypadki sukcesu i wszystkie scenariusze błędów.
8.  **Testy integracyjne**: Dodać testy dla całego endpointu, symulując żądania HTTP i weryfikując odpowiedzi, w tym kody statusu i strukturę danych. Należy zamockować wywołanie serwisu AI.
9.  **Dokumentacja**: Upewnić się, że endpoint jest poprawnie udokumentowany w generowanej automatycznie dokumentacji Swagger/OpenAPI. 