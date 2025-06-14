# API Endpoint Implementation Plan: GET /quizzes/{quiz_id}

## 1. Przegląd punktu końcowego
Ten punkt końcowy służy do pobierania szczegółowych informacji o konkretnym quizie na podstawie jego unikalnego identyfikatora (`quiz_id`). Punkt końcowy wymaga uwierzytelnienia i dostosowuje odpowiedź w zależności od roli użytkownika. Użytkownicy z rolą `admin` otrzymują pełne dane, w tym informacje o poprawności odpowiedzi, podczas gdy użytkownicy z rolą `student` otrzymują te same dane z pominięciem informacji o poprawności odpowiedzi.

## 2. Szczegóły żądania
- **Metoda HTTP**: `GET`
- **Struktura URL**: `/api/v1/quizzes/{quiz_id}`
- **Parametry**:
  - **Wymagane**:
    - `quiz_id` (parametr ścieżki, `int`): Unikalny identyfikator quizu.
  - **Opcjonalne**: Brak.
- **Request Body**: Brak.

## 3. Wykorzystywane typy
- `schemas.QuizReadDetail`: Schemat Pydantic używany do serializacji danych quizu dla użytkowników z rolą `admin`. Zawiera pełne informacje o pytaniach i odpowiedziach, w tym pole `is_correct`.
- `schemas.QuizReadDetailStudent`: Schemat Pydantic używany do serializacji danych quizu dla użytkowników z rolą `student`. Pomija pole `is_correct` w odpowiedziach.
- `schemas.UserRead`: Schemat Pydantic reprezentujący uwierzytelnionego użytkownika, używany do weryfikacji roli.
- `models.Quiz`: Model SQLAlchemy reprezentujący tabelę `quizzes` w bazie danych.

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu (`200 OK`)**:
  - **Dla administratora**: Zwraca obiekt JSON zgodny ze schematem `QuizReadDetail`.
    ```json
    {
      "id": 1,
      "title": "Historia Polski",
      "status": "published",
      "level_id": 1,
      "creator_id": 1,
      "updated_at": "2024-01-01T12:00:00Z",
      "questions": [
          {
              "id": 1,
              "text": "Kto był pierwszym królem Polski?",
              "answers": [
                  {"id": 1, "text": "Mieszko I", "is_correct": false},
                  {"id": 2, "text": "Bolesław Chrobry", "is_correct": true},
                  {"id": 3, "text": "Kazimierz Wielki", "is_correct": false},
                  {"id": 4, "text": "Władysław Łokietek", "is_correct": false}
              ]
          }
      ]
    }
    ```
  - **Dla studenta**: Zwraca obiekt JSON zgodny ze schematem `QuizReadDetailStudent`.
    ```json
    {
      "id": 1,
      "title": "Historia Polski",
      "status": "published",
      "level_id": 1,
      "creator_id": 1,
      "updated_at": "2024-01-01T12:00:00Z",
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
      ]
    }
    ```
- **Odpowiedzi błędów**:
  - `401 Unauthorized`: Użytkownik nie jest uwierzytelniony.
  - `404 Not Found`: Quiz o podanym `quiz_id` nie istnieje.
  - `422 Unprocessable Entity`: `quiz_id` nie jest liczbą całkowitą.

## 5. Przepływ danych
1.  Żądanie `GET` trafia do routera FastAPI `api/v1/quizzes/{quiz_id}`.
2.  FastAPI wstrzykuje zależności: sesję bazy danych (`db: Session`) oraz bieżącego użytkownika (`current_user: models.User`).
3.  Punkt końcowy wywołuje funkcję `quiz_service.get_quiz_by_id(db=db, quiz_id=quiz_id)`.
4.  Serwis `quiz_service` odpytuje bazę danych w poszukiwaniu quizu o zadanym `quiz_id`. Używa `options(selectinload(...))` do efektywnego załadowania powiązanych pytań i odpowiedzi w jednym zapytaniu.
5.  Jeśli quiz nie zostanie znaleziony, serwis zgłasza `HTTPException` ze statusem `404 Not Found`.
6.  Jeśli quiz zostanie znaleziony, jest zwracany do warstwy routera.
7.  W routerze, na podstawie roli `current_user.role`, podejmowana jest decyzja o schemacie odpowiedzi:
    - Jeśli rola to `admin`, odpowiedź jest serializowana przy użyciu `QuizReadDetail`.
    - Jeśli rola to `student`, odpowiedź jest serializowana przy użyciu `QuizReadDetailStudent`.
8.  Zserializowana odpowiedź JSON jest wysyłana do klienta z kodem statusu `200 OK`.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Dostęp do punktu końcowego musi być chroniony. Należy użyć zależności `Depends(get_current_active_user)`, która zweryfikuje token JWT i zwróci aktywny obiekt użytkownika.
- **Autoryzacja**: Logika w punkcie końcowym musi sprawdzać pole `role` obiektu `current_user`. Jest to kluczowe, aby zapobiec wyciekowi danych (pole `is_correct`) do nieautoryzowanych użytkowników (studentów).
- **Walidacja danych wejściowych**: FastAPI automatycznie waliduje typ parametru ścieżki (`quiz_id` musi być typu `int`), co zapobiega atakom typu Path Traversal i SQL Injection na poziomie typu danych.

## 7. Rozważania dotyczące wydajności
- **Zapytania do bazy danych**: Aby uniknąć problemu N+1 zapytań, należy użyć `selectinload` z SQLAlchemy ORM do jednoczesnego załadowania quizu, jego pytań i odpowiedzi w jednym zapytaniu do bazy danych. Przykład: `options(selectinload(models.Quiz.questions).selectinload(models.Question.answers))`.
- **Rozmiar odpowiedzi**: W przypadku quizów z bardzo dużą liczbą pytań, rozmiar odpowiedzi może być duży. Należy rozważyć paginację pytań w przyszłości, jeśli stanie się to problemem. Na obecnym etapie nie jest to wymagane.

## 8. Etapy wdrożenia
1.  **Utworzenie funkcji w serwisie**:
    - W pliku `backend/app/services/quiz_service.py` dodaj nową funkcję `get_quiz_by_id(db: Session, quiz_id: int) -> models.Quiz`.
    - Funkcja powinna pobierać quiz z bazy danych wraz z powiązanymi pytaniami i odpowiedziami, używając `selectinload`.
    - Jeśli quiz nie zostanie znaleziony, funkcja powinna zgłosić `HTTPException(status_code=404, detail="Quiz not found")`.
2.  **Utworzenie testów dla serwisu**:
    - W `backend/app/tests/services/` dodaj testy dla `quiz_service.get_quiz_by_id`, sprawdzając zarówno przypadek sukcesu, jak i przypadek, gdy quiz nie istnieje.
3.  **Utworzenie punktu końcowego w routerze**:
    - W pliku `backend/app/routers/quizzes.py` dodaj nowy punkt końcowy `GET /{quiz_id}`.
    - Zdefiniuj `response_model=None`, aby móc dynamicznie zwracać różne schematy.
    - Dodaj zależności dla sesji DB (`db: Session`) i bieżącego użytkownika (`current_user: models.User`).
4.  **Implementacja logiki w routerze**:
    - Wywołaj `quiz_service.get_quiz_by_id`, aby pobrać dane quizu.
    - Dodaj warunek `if-else` sprawdzający `current_user.role`.
    - Jeśli `current_user.role == 'admin'`, zwróć quiz. FastAPI automatycznie użyje domyślnego schematu `QuizReadDetail` bazując na typie zwrotnym. Można też jawnie użyć `QuizReadDetail.from_orm(quiz)`.
    - Jeśli `current_user.role == 'student'`, przekształć obiekt quizu za pomocą `QuizReadDetailStudent.from_orm(quiz)` i zwróć go.
5.  **Utworzenie testów dla punktu końcowego**:
    - W `backend/app/tests/routers/` dodaj testy dla nowego punktu końcowego.
    - Utwórz testy dla obu ról (admin i student), aby zweryfikować, czy otrzymują prawidłową strukturę odpowiedzi.
    - Dodaj test sprawdzający odpowiedź `404 Not Found`.
    - Dodaj test sprawdzający odpowiedź `401 Unauthorized` dla nieuwierzytelnionego użytkownika.
6.  **Aktualizacja dokumentacji API**:
    - Upewnij się, że FastAPI/Swagger automatycznie generuje poprawną dokumentację dla nowego punktu końcowego. W razie potrzeby dodaj opisy i podsumowania w kodzie routera. 