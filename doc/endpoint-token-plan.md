# API Endpoint Implementation Plan: POST /token

## 1. Przegląd punktu końcowego
Celem tego punktu końcowego jest uwierzytelnienie użytkownika na podstawie jego nazwy użytkownika i hasła. Po pomyślnej weryfikacji tożsamości, punkt końcowy generuje i zwraca token dostępu JWT (`access_token`) typu `bearer`. Ten token będzie używany do autoryzacji w chronionych punktach końcowych API.

## 2. Szczegóły żądania
- **Metoda HTTP**: `POST`
- **Struktura URL**: `/token`
- **Typ ciała żądania**: `application/x-www-form-urlencoded`
- **Pola ciała żądania**:
  - `username` (string, wymagane): Nazwa użytkownika.
  - `password` (string, wymagane): Hasło użytkownika.

## 3. Wykorzystywane typy
- **Żądanie**: `fastapi.security.OAuth2PasswordRequestForm` zostanie użyte jako zależność do automatycznego przechwycenia danych formularza `username` i `password`.
- **Odpowiedź**: `schemas.Token` będzie użyty do strukturyzacji odpowiedzi, zapewniając zgodność z polami `access_token` i `token_type`.

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu**: `200 OK`
  ```json
  {
    "access_token": "your.jwt.token",
    "token_type": "bearer"
  }
  ```
- **Odpowiedź błędu**: `401 Unauthorized`
  ```json
  {
    "detail": "Incorrect username or password"
  }
  ```

## 5. Przepływ danych
1.  Klient wysyła żądanie `POST` na `/token` z `username` i `password` w ciele `x-www-form-urlencoded`.
2.  Funkcja obsługująca punkt końcowy odbiera dane za pomocą zależności `OAuth2PasswordRequestForm`.
3.  Wywoływana jest funkcja serwisowa `authenticate_user(username, password)` (z modułu `core.security` lub `crud.user`).
4.  Funkcja `authenticate_user` wyszukuje użytkownika w tabeli `users` po polu `username`.
    - Jeśli użytkownik nie istnieje, funkcja zwraca `False`.
5.  Jeśli użytkownik istnieje, jego hasło jest weryfikowane za pomocą funkcji `verify_password(plain_password, hashed_password)`, która porównuje hash podanego hasła z hashem z bazy danych.
    - Jeśli hasła się nie zgadzają, funkcja zwraca `False`.
6.  Jeśli uwierzytelnienie w kroku 3-5 nie powiedzie się, punkt końcowy zwraca odpowiedź `401 Unauthorized`.
7.  Jeśli uwierzytelnienie się powiedzie, wywoływana jest funkcja `create_access_token(data={"sub": username})` z `core.security`.
8.  Funkcja `create_access_token` generuje token JWT, kodując w nim nazwę użytkownika oraz datę wygaśnięcia.
9.  Punkt końcowy zwraca odpowiedź `200 OK` z wygenerowanym tokenem w formacie schematu `schemas.Token`.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Mechanizm oparty na JWT.
- **Hashowanie haseł**: Wszystkie hasła w bazie danych muszą być przechowywane jako hashe. Należy użyć biblioteki `passlib` z algorytmem `Bcrypt`.
- **Ochrona przed atakami typu "Timing Attack"**: Porównanie haseł musi być wykonane przy użyciu bezpiecznej funkcji, np. `secrets.compare_digest`, którą `passlib` domyślnie stosuje.
- **Wygasanie tokenów**: Tokeny JWT muszą mieć ustawiony krótki czas życia (np. 30 minut), aby zminimalizować ryzyko w przypadku ich przejęcia.
- **Transport**: Cała komunikacja z API musi odbywać się przez HTTPS, aby chronić dane uwierzytelniające i tokeny przed podsłuchem.
- **Ograniczenie liczby żądań (Rate Limiting)**: Należy rozważyć implementację rate-limitingu na tym punkcie końcowym, aby zapobiec atakom brute-force.

## 7. Obsługa błędów
- **Nieprawidłowe dane uwierzytelniające**: Jeśli `username` nie istnieje lub `password` jest nieprawidłowe, serwer musi zwrócić kod stanu `401 Unauthorized` z komunikatem `{"detail": "Incorrect username or password"}`. Należy unikać podawania, która część (nazwa użytkownika czy hasło) była niepoprawna.
- **Brakujące pola**: FastAPI domyślnie zwróci `422 Unprocessable Entity`, jeśli w żądaniu brakuje `username` lub `password`. Należy to przechwycić i ujednolicić odpowiedź do `401 Unauthorized`, aby nie ujawniać szczegółów implementacji.

## 8. Rozważania dotyczące wydajności
- **Indeksowanie bazy danych**: Kolumna `username` w tabeli `users` musi być zindeksowana (jest `UNIQUE`, więc domyślnie powinna mieć indeks), aby zapewnić szybkie wyszukiwanie użytkowników.
- **Złożoność hashowania**: Obliczenia związane z hashowaniem (Bcrypt) są celowo kosztowne. Należy to uwzględnić przy planowaniu skalowalności systemu uwierzytelniania. Nie stanowi to problemu przy typowym obciążeniu, ale może być istotne przy masowych atakach.

## 9. Etapy wdrożenia
1.  **Dodanie zależności**: Upewnij się, że w pliku `requirements.txt` znajdują się biblioteki: `python-jose[cryptography]` (do obsługi JWT) oraz `passlib[bcrypt]` (do hashowania haseł).
2.  **Konfiguracja**: W pliku `core/config.py` dodaj zmienne konfiguracyjne dla JWT: `SECRET_KEY`, `ALGORITHM` i `ACCESS_TOKEN_EXPIRE_MINUTES`.
3.  **Utworzenie modułu CRUD dla użytkownika**: W `backend/app/crud/user.py` stwórz funkcję `get_user_by_username(db: Session, username: str)`, która pobierze użytkownika z bazy danych.
4.  **Rozbudowa modułu `security`**: W `backend/app/core/security.py` zaimplementuj:
    - `OAuth2PasswordBearer` scheme.
    - Funkcje `verify_password(plain_password, hashed_password)` i `get_password_hash(password)`.
    - Funkcję `create_access_token(data: dict, ...)`.
    - Funkcję `authenticate_user(db: Session, username: str, password: str)`. Powinna ona wykorzystywać `crud.user.get_user_by_username` oraz `verify_password`.
5.  **Utworzenie routera**: Stwórz nowy plik routera `backend/app/routers/token.py`.
6.  **Implementacja punktu końcowego**: W `routers/token.py` zdefiniuj ścieżkę `POST /token`:
    - Dodaj zależności `db: Session = Depends(get_db)` i `form_data: OAuth2PasswordRequestForm = Depends()`.
    - Wywołaj `security.authenticate_user`, przekazując `db` i dane z `form_data`.
    - W przypadku błędu uwierzytelniania, rzuć `HTTPException` z kodem `401`.
    - Jeśli uwierzytelnianie się powiedzie, wywołaj `security.create_access_token`.
    - Zwróć obiekt `schemas.Token`.
7.  **Rejestracja routera**: W `main.py` zaimportuj i zarejestruj nowy router `token_router`.
8.  **Testy**: Napisz testy jednostkowe i integracyjne dla przepływu uwierzytelniania, obejmujące zarówno pomyślne logowanie, jak i przypadki błędów. 