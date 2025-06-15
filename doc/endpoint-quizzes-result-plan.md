# API Endpoint Implementation Plan: POST /quizzes/{quiz_id}/results

## 1. Przegląd punktu końcowego
Ten punkt końcowy umożliwia uwierzytelnionemu użytkownikowi z rolą "student" przesłanie wyniku za ukończony quiz. System zapisuje wynik w bazie danych. Jeśli student ukończył już ten quiz wcześniej, istniejący wynik zostanie zaktualizowany; w przeciwnym razie zostanie utworzony nowy wpis.

## 2. Szczegóły żądania
- **Metoda HTTP**: `POST`
- **Struktura URL**: `/quizzes/{quiz_id}/results`
- **Parametry**:
  - **Wymagane**:
    - `quiz_id` (w ścieżce, int): Unikalny identyfikator quizu.
  - **Opcjonalne**: Brak.
- **Ciało żądania (Request Body)**:
  ```json
  {
    "score": 8,
    "max_score": 10
  }
  ```
  - `score` (int, wymagane): Liczba punktów zdobytych przez studenta.
  - `max_score` (int, wymagane): Całkowita możliwa liczba punktów do zdobycia w quizie.

## 3. Wykorzystywane typy
- **Ciało żądania (Input)**: `schemas.ResultCreate`
- **Odpowiedź (Output)**: `schemas.ResultRead`

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu**: `201 Created`. Zwraca nowo utworzony lub zaktualizowany obiekt wyniku.
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
- **Odpowiedzi błędu**:
  - `401 Unauthorized`
  - `403 Forbidden`
  - `404 Not Found`
  - `422 Unprocessable Entity`
  - `500 Internal Server Error`

## 5. Przepływ danych
1.  Użytkownik wysyła żądanie `POST` na adres `/quizzes/{quiz_id}/results` z tokenem uwierzytelniającym i ciałem żądania.
2.  System (FastAPI) weryfikuje token JWT i rolę użytkownika ('student') za pomocą wstrzykiwanej zależności.
3.  FastAPI waliduje typ `quiz_id` (int) oraz ciało żądania przy użyciu schematu Pydantic `ResultCreate`.
4.  Endpoint pobiera z bazy danych quiz o podanym `quiz_id`. Jeśli nie istnieje, zwraca `404 Not Found`.
5.  Endpoint pobiera liczbę pytań dla danego quizu i porównuje ją z `max_score` z żądania. Jeśli wartości się nie zgadzają, zwraca `422 Unprocessable Entity`.
6.  Endpoint weryfikuje, czy `score <= max_score`. Jeśli nie, zwraca `422 Unprocessable Entity`.
7.  System sprawdza, czy w tabeli `results` istnieje już wpis dla `user_id` (z tokena) i `quiz_id`.
8.  - **Jeśli wynik istnieje**: System aktualizuje istniejący rekord w tabeli `results` nowymi wartościami `score`,`max_score` i `updated_at`.
    - **Jeśli wynik nie istnieje**: System tworzy nowy rekord w tabeli `results`, używając `user_id`, `quiz_id` oraz danych z ciała żądania.
9.  System zwraca odpowiedź `201 Created` wraz z danymi utworzonego/zaktualizowanego wyniku (zgodnie ze schematem `ResultRead`).

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Dostęp do punktu końcowego jest chroniony. Wymagany jest prawidłowy token JWT.
- **Autoryzacja**: Tylko użytkownicy z rolą `student` mogą przesyłać wyniki. Należy zaimplementować mechanizm sprawdzania ról.
- **Integralność danych**: `user_id` do zapisu wyniku jest pobierany wyłącznie z tokena JWT, aby uniemożliwić studentowi przesłanie wyniku w imieniu innej osoby.
- **Walidacja po stronie serwera**: Wszystkie dane wejściowe (`quiz_id`, `score`, `max_score`) są rygorystycznie walidowane po stronie serwera w celu uniknięcia niespójności danych.

## 7. Obsługa błędów
- `401 Unauthorized`: Token JWT jest nieprawidłowy lub nie został dostarczony.
- `403 Forbidden`: Użytkownik jest uwierzytelniony, ale jego rola jest inna niż `student`.
- `404 Not Found`: Quiz o podanym `quiz_id` nie został znaleziony w bazie danych.
- `422 Unprocessable Entity`:
  - Ciało żądania nie przechodzi walidacji Pydantic (np. `score < 0`).
  - `score` jest większe niż `max_score`.
  - `max_score` z żądania nie odpowiada rzeczywistej liczbie pytań w quizie.
- `500 Internal Server Error`: Wystąpił nieoczekiwany błąd serwera, np. problem z połączeniem z bazą danych.

## 8. Rozważania dotyczące wydajności
- Operacje na bazie danych (pobranie quizu, pobranie/wstawienie/aktualizacja wyniku) opierają się na indeksowanych kolumnach (`id`, `user_id`, `quiz_id`), co zapewnia wysoką wydajność.
- Obciążenie tego punktu końcowego nie powinno być znaczące, więc nie przewiduje się problemów z wydajnością przy standardowym użytkowaniu.

## 9. Etapy wdrożenia
1.  **Aktualizacja schematów (Schemas)**:
    - Upewnij się, że schematy `ResultCreate` i `ResultRead` w `backend/app/schemas/result.py` są zgodne z wymaganiami.
2.  **Warstwa dostępu do danych (CRUD)**:
    - Utwórz plik `backend/app/crud/result.py`.
    - Zaimplementuj funkcję `get_by_user_and_quiz(db, user_id, quiz_id)` do pobierania istniejącego wyniku.
    - Zaimplementuj funkcję `create_with_owner(db, obj_in, user_id, quiz_id)` do tworzenia nowego wyniku.
    - Zaimplementuj funkcję `update(db, db_obj, obj_in)` do aktualizacji istniejącego wyniku.
3.  **Router (Endpoint)**:
    - Dodaj nowy endpoint `POST /quizzes/{quiz_id}/results` w pliku `backend/app/routers/quizzes.py` (lub w nowym `results.py`).
    - Zaimplementuj logikę endpointu, włączając w to:
      - Wstrzyknięcie zależności `db: Session` i `current_user: models.User`.
      - Sprawdzenie roli użytkownika (`student`).
      - Pobranie i walidację quizu.
      - Walidację `score` i `max_score`.
      - Wywołanie odpowiednich funkcji CRUD w celu utworzenia lub aktualizacji wyniku.
      - Zwrócenie odpowiedzi `201 Created` z danymi wyniku.
4.  **Integracja z główną aplikacją**:
    - Jeśli został utworzony nowy plik routera, zamontuj go w `backend/app/main.py`.
5.  **Testy**:
    - Napisz testy jednostkowe i integracyjne dla nowego punktu końcowego, obejmujące:
      - Scenariusz pomyślny (utworzenie i aktualizacja wyniku).
      - Wszystkie zdefiniowane scenariusze błędów (401, 403, 404, 422).
      - Przypadki brzegowe walidacji. 