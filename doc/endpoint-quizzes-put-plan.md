# API Endpoint Implementation Plan: PUT /quizzes/{quiz_id}

## 1. Przegląd punktu końcowego
Ten punkt końcowy umożliwia administratorom kompleksową aktualizację istniejącego quizu. Pozwala na modyfikację jego podstawowych atrybutów (tytuł, poziom trudności), zmianę statusu z `draft` na `published`, a także na dodawanie, usuwanie i edytowanie pytań oraz ich odpowiedzi w ramach pojedynczego żądania.

## 2. Szczegóły żądania
- **Metoda HTTP:** `PUT`
- **Struktura URL:** `/quizzes/{quiz_id}`
- **Parametry:**
  - **Ścieżki:**
    - `quiz_id` (int, wymagany): Unikalny identyfikator quizu do aktualizacji.
  - **Ciała żądania (Request Body):**
    - `title` (str, wymagany): Nowy tytuł quizu.
    - `level_id` (int, wymagany): Identyfikator poziomu trudności.
    - `status` (str, opcjonalny): Nowy status quizu. Dozwolone wartości: `draft`, `published`.
    - `questions` (list[object], wymagany): Lista obiektów pytań.
- **Struktura ciała żądania (Request Body):**
  ```json
  {
    "title": "Nowy Tytuł Quizu",
    "status": "published",
    "level_id": 4,
    "questions": [
      {
        "id": 1, 
        "text": "Zaktualizowane pytanie?",
        "answers": [
          {"id": 1, "text": "Zmieniona odp A", "is_correct": false},
          {"id": 2, "text": "Zmieniona odp B", "is_correct": true}
        ]
      },
      {
        "text": "Nowe pytanie?", 
        "answers": [
            {"text": "Nowa odp A", "is_correct": true}
        ]
      }
    ]
  }
  ```

## 3. Wykorzystywane typy
- **Żądanie:** `schemas.QuizUpdate`, `schemas.QuestionUpdate`. Konieczne może być dostosowanie schematów, aby umożliwić dodawanie pytań i odpowiedzi bez `id`. Proponuje się, aby pole `answers` w `QuestionUpdate` oraz `questions` w `QuizUpdate` przyjmowały unię typów, np. `List[Union[QuestionUpdate, QuestionCreate]]`.
- **Odpowiedź:** `schemas.QuizReadDetail` - Zwraca pełny, zaktualizowany obiekt quizu wraz ze wszystkimi pytaniami i odpowiedziami.

## 4. Szczegóły odpowiedzi
- **Sukces:** `200 OK` z ciałem odpowiedzi zawierającym zaktualizowany obiekt quizu w formacie `QuizReadDetail`.
- **Błędy:** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`.

## 5. Przepływ danych
1.  Użytkownik (admin) wysyła żądanie `PUT` na adres `/quizzes/{quiz_id}`.
2.  Middleware FastAPI weryfikuje token JWT (uwierzytelnianie).
3.  Zależność (dependency) weryfikuje rolę użytkownika (autoryzacja 'admin').
4.  Zależność (dependency) waliduje ciało żądania względem schematu Pydantic `QuizUpdate`.
5.  Router wywołuje funkcję serwisową, np. `quiz_service.update_quiz()`, przekazując `db_session`, `quiz_id` oraz dane z ciała żądania.
6.  Serwis rozpoczyna transakcję bazodanową.
7.  Serwis pobiera z bazy danych quiz o podanym `quiz_id`. Jeśli nie istnieje, zwraca błąd `404`.
8.  Serwis aktualizuje podstawowe pola quizu: `title`, `level_id`, `status`.
9.  Serwis pobiera listę ID istniejących pytań z payloadu i porównuje ją z listą pytań w quizie z bazy danych, aby zidentyfikować pytania do usunięcia.
10. Pytania, które istnieją w bazie, a nie ma ich w żądaniu, są usuwane (kaskadowo z odpowiedziami).
11. Serwis iteruje po liście pytań z żądania:
    - Jeśli pytanie ma `id`, jest aktualizowane. Odpowiedzi są przetwarzane w analogiczny sposób (aktualizacja, dodawanie, usuwanie).
    - Jeśli pytanie nie ma `id`, jest tworzone jako nowy rekord powiązany z quizem, wraz z nowymi odpowiedziami.
12. Transakcja jest zatwierdzana (commit).
13. Serwis pobiera zaktualizowany obiekt quizu z bazy i zwraca go do routera.
14. Router zwraca odpowiedź `200 OK` z obiektem quizu.
15. W przypadku jakiegokolwiek błędu walidacji lub błędu bazy danych, transakcja jest wycofywana (rollback), a odpowiedni kod błędu HTTP jest zwracany.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie:** Endpoint musi być chroniony przez mechanizm JWT. Żądania bez ważnego tokenu będą odrzucane z kodem `401`.
- **Autoryzacja:** Dostęp musi być ograniczony do użytkowników z rolą `admin`. Próba dostępu przez innego użytkownika zwróci błąd `403`.
- **Walidacja:**
    - Wszystkie dane wejściowe są walidowane przez Pydantic pod kątem typu i struktury.
    - Logika biznesowa w serwisie musi weryfikować, czy `quiz_id` i `level_id` istnieją.
    - Należy upewnić się, że identyfikatory pytań i odpowiedzi (`question.id`, `answer.id`) w żądaniu należą do aktualizowanego quizu, aby zapobiec modyfikacji danych w innych quizach.

## 7. Obsługa błędów
- **`401 Unauthorized`**: Brak lub nieważny token uwierzytelniający.
- **`403 Forbidden`**: Użytkownik nie posiada uprawnień administratora.
- **`404 Not Found`**:
    - Quiz o podanym `{quiz_id}` nie został znaleziony.
    - `level_id` podany w ciele żądania nie istnieje w bazie danych.
- **`422 Unprocessable Entity`**:
    - Błąd walidacji Pydantic (np. `title` jest pusty, `is_correct` nie jest booleanem).
    - Niespełniona reguła biznesowa (np. każde pytanie musi mieć co najmniej jedną poprawną odpowiedź).
- **`500 Internal Server Error`**: Wewnętrzny błąd serwera, np. błąd podczas zatwierdzania transakcji w bazie danych.

## 8. Rozważania dotyczące wydajności
- Wszystkie operacje na bazie danych (UPDATE, INSERT, DELETE) muszą być opakowane w jedną transakcję, aby zapewnić spójność danych (atomowość) i zminimalizować liczbę zapytań do bazy.
- Należy unikać nadmiarowych zapytań do bazy w pętlach (problem N+1). Pytania i odpowiedzi do quizu powinny być pobierane za pomocą jednego zapytania z użyciem `joinedload` lub `selectinload` z SQLAlchemy.

## 9. Etapy wdrożenia
1.  **Modyfikacja Schematów Pydantic:**
    - Zaktualizuj schemat `schemas.QuizUpdate`, aby pole `questions` przyjmowało listę obiektów, które mogą mieć `id` (dla aktualizacji) lub nie (dla tworzenia). Podobnie dla pola `answers` w `schemas.QuestionUpdate`. Można użyć `Union` lub stworzyć dedykowane schematy.
2.  **CRUD Layer:**
    - Upewnij się, że istnieją lub dodaj funkcje CRUD do usuwania pytań i odpowiedzi (np. `crud.question.remove_many_by_ids`).
    - Upewnij się, że funkcje do aktualizacji i tworzenia są dostępne i wydajne.
3.  **Service Layer (`quiz_service.py`):**
    - Stwórz funkcję `update_quiz(db: Session, quiz_id: int, data: schemas.QuizUpdate) -> models.Quiz`.
    - Zaimplementuj w niej pełną logikę opisaną w sekcji "Przepływ danych", włączając w to zarządzanie transakcjami.
4.  **Router Layer (`quizzes.py`):**
    - Stwórz endpoint `PUT /quizzes/{quiz_id}`.
    - Dodaj zależności (dependencies) do uwierzytelniania i autoryzacji (`get_current_active_admin`).
    - Wywołaj funkcję z warstwy serwisowej i zwróć wynik.
5.  **Testy:**
    - Napisz testy jednostkowe dla logiki w warstwie serwisowej.
    - Napisz testy integracyjne dla endpointu, które pokryją:
        - Poprawny scenariusz aktualizacji.
        - Dodawanie, usuwanie i modyfikację pytań/odpowiedzi.
        - Scenariusze błędów (401, 403, 404, 422).
        - Przypadki brzegowe (np. wysłanie pustej listy pytań).
