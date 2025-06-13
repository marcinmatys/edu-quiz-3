# API Endpoint Implementation Plan: GET /users/me

## 1. Przegląd punktu końcowego
Ten punkt końcowy służy do pobierania informacji o profilu aktualnie uwierzytelnionego użytkownika. Użytkownik jest identyfikowany na podstawie tokena JWT dostarczonego w nagłówku autoryzacyjnym. Zwracane są tylko dane publiczne, z wyłączeniem informacji wrażliwych, takich jak hasło.

## 2. Szczegóły żądania
- **Metoda HTTP**: `GET`
- **Struktura URL**: `/api/v1/users/me`
- **Parametry**:
  - **Wymagane**:
    - Nagłówek: `Authorization: Bearer <JWT_TOKEN>`
  - **Opcjonalne**: Brak
- **Request Body**: Brak

## 3. Wykorzystywane typy
- **Schemat odpowiedzi (Pydantic)**: `schemas.UserRead`
  ```python
  class UserRead(UserBase):
      id: int
      role: str
      created_at: datetime
      
      model_config = ConfigDict(from_attributes=True)
  ```

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu**: `200 OK`
  - **Treść**: Obiekt JSON zgodny ze schematem `schemas.UserRead`.
  ```json
  {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2023-10-27T10:00:00Z"
  }
  ```
- **Odpowiedzi błędów**:
  - `401 Unauthorized`: W przypadku braku, nieważności lub wygaśnięcia tokena uwierzytelniającego.

## 5. Przepływ danych
1. Klient wysyła żądanie `GET` na adres `/api/v1/users/me` z prawidłowym tokenem JWT w nagłówku `Authorization`.
2. FastAPI wywołuje zależność `get_current_user`, która jest odpowiedzialna за proces uwierzytelniania.
3. Zależność `get_current_user` dekoduje i weryfikuje token JWT.
4. Po pomyślnej weryfikacji, z tokena wyodrębniany jest identyfikator użytkownika (`user_id`).
5. Zależność wykonuje zapytanie do bazy danych, aby pobrać obiekt `models.User` na podstawie `user_id`.
6. Obiekt `models.User` jest wstrzykiwany jako argument do funkcji obsługującej punkt końcowy.
7. Funkcja zwraca otrzymany obiekt `models.User`.
8. FastAPI automatycznie konwertuje obiekt SQLAlchemy `models.User` na słownik, a następnie na JSON, zgodnie ze schematem `schemas.UserRead` zdefiniowanym w `response_model`.
9. Odpowiedź JSON jest wysyłana do klienta z kodem statusu `200 OK`.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Uwierzytelnianie jest obowiązkowe i realizowane za pomocą tokenów JWT. Należy stworzyć lub zweryfikować istnienie solidnej zależności `get_current_user`, która obsługuje cały proces walidacji tokena.
- **Autoryzacja**: Dostęp do tego punktu końcowego ma każdy uwierzytelniony użytkownik (niezależnie od roli `admin` czy `student`), ale może on pobrać tylko własne dane.
- **Walidacja danych**: Schemat odpowiedzi `UserRead` zapewnia, że żadne wrażliwe dane (np. `hashed_password`) nie zostaną ujawnione w odpowiedzi API.

## 7. Obsługa błędów
- **Brak tokena lub nieprawidłowy format**: Zależność `get_current_user` powinna zgłosić `HTTPException` ze statusem `401` i odpowiednim komunikatem.
- **Token nieważny lub wygasł**: Zależność `get_current_user` powinna zgłosić `HTTPException` ze statusem `401`.
- **Użytkownik nie znaleziony w bazie danych**: Jeśli token jest ważny, ale odpowiadający mu użytkownik został usunięty, zależność powinna również zgłosić `HTTPException` ze statusem `401`.
- **Błąd serwera**: W przypadku problemów z połączeniem z bazą danych lub innych nieoczekiwanych błędów, FastAPI zwróci domyślną odpowiedź `500 Internal Server Error`.

## 8. Rozważania dotyczące wydajności
- Zapytanie do bazy danych jest proste (wyszukiwanie po kluczu głównym), więc oczekuje się wysokiej wydajności.
- Nie przewiduje się wąskich gardeł. Buforowanie (caching) nie jest konieczne na tym etapie, ale można je rozważyć w przyszłości, jeśli punkt końcowy będzie poddawany ekstremalnemu obciążeniu.

## 9. Etapy wdrożenia
1. **Utworzenie/Weryfikacja zależności**: Sprawdź, czy w `backend/app/core/auth.py` (lub podobnej lokalizacji) istnieje funkcja zależności `get_current_user`. Jeśli nie, należy ją zaimplementować. Musi ona obsługiwać dekodowanie JWT, walidację i pobieranie użytkownika z bazy danych.
2. **Utworzenie routera**: Utwórz nowy plik `backend/app/routers/users.py` dla punktów końcowych związanych z użytkownikami.
3. **Zdefiniowanie routera**: W `backend/app/routers/users.py` utwórz instancję `APIRouter`.
   ```python
   from fastapi import APIRouter
   router = APIRouter()
   ```
4. **Implementacja punktu końcowego**: W tym samym pliku zaimplementuj funkcję dla punktu końcowego `GET /me`.
   ```python
   from fastapi import Depends
   from sqlalchemy.orm import Session
   from backend.app import models, schemas
   from backend.app.core.auth import get_current_user # Przykład importu
   from backend.app.db.session import get_db

   @router.get("/me", response_model=schemas.UserRead)
   def read_users_me(current_user: models.User = Depends(get_current_user)):
       """
       Get current user.
       """
       return current_user
   ```
5. **Rejestracja routera**: W głównym pliku aplikacji `backend/app/main.py` dołącz nowo utworzony router.
   ```python
   from backend.app.routers import users
   
   # ...
   
   app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
   ```
6. **Testowanie**: Utwórz testy jednostkowe i integracyjne, które zweryfikują:
   - Poprawne pobieranie danych użytkownika z prawidłowym tokenem.
   - Zwracanie błędu `401` dla żądań bez tokena.
   - Zwracanie błędu `401` dla żądań z nieprawidłowym lub wygasłym tokenem. 