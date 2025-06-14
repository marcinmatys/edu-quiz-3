# API Endpoint Implementation Plan: GET /levels

## 1. Przegląd punktu końcowego
Celem tego punktu końcowego jest dostarczenie klientowi listy wszystkich dostępnych poziomów trudności quizów. Dostęp jest ograniczony tylko dla uwierzytelnionych użytkowników.

## 2. Szczegóły żądania
- **Metoda HTTP**: `GET`
- **Struktura URL**: `/api/v1/levels`
- **Parametry**:
  - **Wymagane**: Brak
  - **Opcjonalne**: Brak
- **Request Body**: Brak

## 3. Wykorzystywane typy
- `schemas.LevelRead`: Do walidacji i serializacji danych wyjściowych dla każdego poziomu na liście.

## 4. Szczegóły odpowiedzi
- **Success Response (`200 OK`)**: Zwraca tablicę JSON, gdzie każdy obiekt reprezentuje jeden poziom trudności.
  ```json
  [
    {
      "id": 1,
      "code": "I",
      "description": "Klasa I",
      "level": 1
    },
    {
      "id": 2,
      "code": "II",
      "description": "Klasa II",
      "level": 2
    }
  ]
  ```
- **Error Responses**:
  - `401 Unauthorized`: W przypadku, gdy żądanie nie zawiera prawidłowego tokenu uwierzytelniającego.
  - `500 Internal Server Error`: W przypadku wystąpienia błędu serwera podczas pobierania danych.

## 5. Przepływ danych
1. Klient wysyła żądanie `GET` na adres `/api/v1/levels`, dołączając token uwierzytelniający (JWT) w nagłówku `Authorization`.
2. Router FastAPI przechwytuje żądanie.
3. Uruchamiana jest zależność (dependency) odpowiedzialna za weryfikację tokenu JWT i autoryzację użytkownika.
4. Jeśli uwierzytelnianie się powiedzie, funkcja obsługująca punkt końcowy wywołuje metodę `crud.level.get_multi()` w celu pobrania wszystkich poziomów z bazy danych.
5. Warstwa CRUD (SQLAlchemy) wykonuje zapytanie `SELECT * FROM levels;`.
6. Baza danych zwraca listę rekordów poziomów.
7. Dane są serializowane przy użyciu schematu Pydantic `LevelRead`.
8. Serwer wysyła odpowiedź HTTP `200 OK` z serializowanymi danymi w formacie JSON.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Dostęp do punktu końcowego musi być zabezpieczony. Zostanie to zaimplementowane przy użyciu zależności FastAPI (np. `Depends(get_current_user)`), która zweryfikuje poprawność tokenu JWT.
- **Autoryzacja**: Specyfikacja nie wymaga specyficznych ról (np. 'admin' czy 'student'). Każdy uwierzytelniony użytkownik może uzyskać dostęp do tej listy.
- **Walidacja danych**: Ponieważ punkt końcowy nie przyjmuje żadnych danych wejściowych, walidacja po stronie serwera nie jest konieczna.

## 7. Rozważania dotyczące wydajności
- Liczba poziomów trudności jest niewielka i rzadko ulega zmianie. W związku z tym, proste zapytanie do bazy danych jest w pełni wystarczające i nie przewiduje się problemów z wydajnością.
- W przyszłości, w przypadku wzrostu obciążenia, można rozważyć implementację mechanizmu buforowania (caching) dla tego zasobu na poziomie serwera (np. przy użyciu `fastapi-cache`).

## 8. Etapy wdrożenia
1.  **Dodanie logiki CRUD**: Upewnić się, że istnieją odpowiednie funkcje CRUD dla poziomów w `backend/app/crud/`

2. **Utworzenie routera dla poziomów**:
   - Stwórz nowy plik `backend/app/routers/levels.py`.
   - Zdefiniuj w nim nowy `APIRouter` z prefixem `/levels` i tagiem `levels`.

3. **Implementacja punktu końcowego**:
   - W `backend/app/routers/levels.py`, utwórz funkcję dla ścieżki `GET /` z dekoratorem `@router.get("/")`.
   - Ustaw `response_model=List[schemas.LevelRead]`.
   - Dodaj zależność `db: Session = Depends(deps.get_db)` oraz zależność do uwierzytelniania, np. `current_user: models.User = Depends(deps.get_current_active_user)`.
   - W ciele funkcji wywołaj `crud.level.get_multi(db=db)` i zwróć wynik.

4. **Rejestracja nowego routera**:
   - W głównym pliku aplikacji `backend/app/main.py`, zaimportuj router `levels` i zarejestruj go w aplikacji FastAPI za pomocą `app.include_router(levels.router)`.

5. **Napisanie testów**:
   - Utwórz testy jednostkowe i integracyjne dla nowego punktu końcowego, aby zweryfikować poprawność działania, obsługę błędów i zabezpieczenia. Sprawdź scenariusze z poprawnym uwierzytelnieniem oraz bez niego. 