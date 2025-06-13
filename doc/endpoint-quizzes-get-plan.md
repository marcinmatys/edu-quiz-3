# API Endpoint Implementation Plan: GET /quizzes

## 1. Przegląd punktu końcowego
Ten punkt końcowy (`endpoint`) jest odpowiedzialny za pobieranie listy quizów. Działa w oparciu o role użytkowników:
- **Administratorzy** mogą przeglądać wszystkie quizy (zarówno w wersji roboczej, jak i opublikowane) oraz korzystać z zaawansowanego sortowania i filtrowania.
- **Studenci** widzą tylko opublikowane quizy. Dla każdego quizu, który już rozwiązali, widzą swój ostatni wynik.

## 2. Szczegóły żądania
- **Metoda HTTP**: `GET`
- **Struktura URL**: `/api/v1/quizzes`
- **Parametry zapytania (Query Parameters)**:
  - `sort_by` (opcjonalny):
    - **Typ**: `string`
    - **Domyślnie**: `'level'`
    - **Dozwolone wartości**: `'level'`, `'title'`, `'updated_at'`
    - **Opis**: Określa pole, po którym wyniki będą sortowane. Sortowanie po `'level'` odbywa się na podstawie numerycznej wartości poziomu, a nie jego kodu.
  - `order` (opcjonalny):
    - **Typ**: `string`
    - **Domyślnie**: `'asc'`
    - **Dozwolone wartości**: `'asc'`, `'desc'`
    - **Opis**: Określa porządek sortowania (rosnący lub malejący).
  - `status` (opcjonalny, **tylko dla administratorów**):
    - **Typ**: `string`
    - **Dozwolone wartości**: `'draft'`, `'published'`
    - **Opis**: Filtruje quizy po ich statusie. Jeśli parametr zostanie użyty przez studenta, zostanie zignorowany.

## 3. Wykorzystywane typy
Do implementacji tego punktu końcowego wykorzystane zostaną następujące schematy Pydantic z modułu `backend/app/schemas/`:
- **`schemas.QuizReadList`**: Główny schemat odpowiedzi dla pojedynczego quizu na liście. Zawiera dynamicznie obliczaną liczbę pytań (`question_count`) oraz opcjonalne dane o ostatnim wyniku.
- **`schemas.LastResult`**: Schemat zagnieżdżony w `QuizReadList`, zawierający wynik (`score`) i maksymalną możliwą liczbę punktów (`max_score`) dla ostatniego podejścia studenta.
- **`models.User`**: Obiekt zalogowanego użytkownika, dostarczany przez zależność, w celu weryfikacji roli.

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu (`200 OK`)**: Zwraca tablicę obiektów zgodnych ze schematem `QuizReadList`.
  ```json
  [
    {
      "id": 1,
      "title": "Historia Polski",
      "status": "published",
      "level_id": 5,
      "creator_id": 1,
      "question_count": 10,
      "last_result": {
        "score": 8,
        "max_score": 10
      },
      "updated_at": "2023-10-27T12:00:00Z"
    }
  ]
  ```
- **Odpowiedzi błędów**:
  - `400 Bad Request`: Nieprawidłowa wartość jednego z parametrów zapytania.
  - `401 Unauthorized`: Użytkownik jest niezalogowany (brak lub niepoprawny token JWT).
  - `500 Internal Server Error`: Wewnętrzny błąd serwera, np. problem z połączeniem z bazą danych.

## 5. Przepływ danych
1.  Żądanie `GET` trafia do routera `/api/v1/quizzes`.
2.  Zależność `get_current_active_user` weryfikuje token JWT i dostarcza obiekt `current_user`.
3.  Endpoint wywołuje funkcję serwisową (np. `quiz_service.get_quizzes`) przekazując sesję DB, obiekt użytkownika i zwalidowane parametry zapytania.
4.  Funkcja serwisowa konstruuje zapytanie SQLAlchemy do tabeli `quizzes`.
5.  Zapytanie jest rozbudowywane o:
    -   **Obliczenie `question_count`**: Podzapytanie zliczające powiązane rekordy w tabeli `questions`.
    -   **Pobranie `last_result` (dla studenta)**: `LEFT JOIN` z tabelą `results` na podstawie `quiz_id` i `user_id` zalogowanego studenta.
    -   **Filtrowanie oparte na roli**:
        -   Dla **studenta**: `WHERE status = 'published'`.
        -   Dla **admina**: opcjonalny filtr `WHERE status = :status`, jeśli podano parametr.
    -   **Sortowanie**: `JOIN` z tabelą `levels` (dla `sort_by='level'`) i dynamiczne dodanie `ORDER BY` na podstawie parametrów `sort_by` i `order`.
6.  Baza danych wykonuje finalne zapytanie.
7.  Wyniki są mapowane na listę obiektów `schemas.QuizReadList`.
8.  Router zwraca listę jako odpowiedź JSON z kodem statusu `200 OK`.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Każde żądanie musi zawierać prawidłowy nagłówek `Authorization: Bearer <token>`. Weryfikacja tokena jest realizowana przez globalną zależność FastAPI.
- **Autoryzacja**: Logika w warstwie serwisowej sprawdza pole `current_user.role`, aby dostosować zapytanie do bazy danych. Gwarantuje to, że studenci widzą tylko opublikowane quizy, a administratorzy mają dostęp do wszystkich danych i opcji filtrowania.
- **Walidacja danych wejściowych**: Parametry `order` i `status` będą walidowane przy użyciu `typing.Literal` lub `enum.Enum` w definicji endpointu. Parametr `sort_by` będzie sprawdzany względem predefiniowanej listy dozwolonych pól w celu ochrony przed nieautoryzowanym dostępem do danych.

## 7. Rozważania dotyczące wydajności
- **Indeksowanie bazy danych**: Należy upewnić się, że kolumny używane w klauzulach `JOIN`, `WHERE` i `ORDER BY` są odpowiednio zindeksowane. Kluczowe kolumny to `quizzes.status`, `quizzes.level_id`, `results.user_id`, `results.quiz_id` oraz `levels.level`.
- **Optymalizacja zapytań**: Zapytanie powinno być tak skonstruowane, aby unikać problemu N+1. Użycie `JOIN` oraz skorelowanych podzapytań pozwoli na pobranie wszystkich potrzebnych danych w jednym zapytaniu do bazy.
- **Paginacja**: Chociaż nie jest to częścią obecnej specyfikacji, w przyszłości należy rozważyć dodanie paginacji, aby efektywnie zarządzać dużymi zbiorami danych.

## 8. Etapy wdrożenia
1.  **Struktura plików**: Utworzyć plik `backend/app/routers/quizzes.py` oraz `backend/app/services/quiz_service.py`, jeśli nie istnieją.
2.  **Definicja routera**: W `quizzes.py` zdefiniować endpoint `GET /` z modelem odpowiedzi `response_model=List[schemas.QuizReadList]`.
3.  **Parametry zapytania**: Zdefiniować parametry zapytania (`sort_by`, `order`, `status`) przy użyciu `fastapi.Query` i typów walidujących (`Literal` lub `Enum`).
4.  **Zależności**: Wstrzyknąć zależności `db: Session` oraz `current_user: models.User`.
5.  **Warstwa serwisowa**: W `quiz_service.py` zaimplementować funkcję `get_all_quizzes(db: Session, user: models.User, sort_by: str, order: str, status: Optional[str]) -> List[models.Quiz]`.
6.  **Implementacja logiki zapytania**: Wewnątrz `get_all_quizzes`:
    -   Zbudować bazowe zapytanie SQLAlchemy.
    -   Dodać podzapytanie do obliczenia `question_count`.
    -   Implementować `LEFT JOIN` do pobrania `last_result` dla studentów.
    -   Dodać warunki `WHERE` w zależności od roli użytkownika i parametru `status`.
    -   Zaimplementować dynamiczne sortowanie, w tym `JOIN` z `levels` dla `sort_by='level'`.
7.  **Połączenie warstw**: Wywołać funkcję serwisową z poziomu routera i zwrócić jej wynik.
8.  **Rejestracja routera**: W `backend/app/main.py` dodać nowy router `quizzes_router` do aplikacji FastAPI.
9.  **Testy**: Napisać testy jednostkowe i integracyjne, które weryfikują:
    -   Poprawność danych dla ról 'admin' i 'student'.
    -   Działanie wszystkich opcji sortowania i filtrowania.
    -   Obsługę przypadków brzegowych i błędów.
    -   Poprawne dołączanie danych `last_result`. 