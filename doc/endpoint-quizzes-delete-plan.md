# API Endpoint Implementation Plan: DELETE /quizzes/{quiz_id}

## 1. Przegląd punktu końcowego
Ten punkt końcowy umożliwia administratorowi trwałe usunięcie quizu wraz ze wszystkimi powiązanymi z nim zasobami, takimi jak pytania, odpowiedzi i wyniki. Operacja jest nieodwracalna i wymaga uprawnień administratora.

## 2. Szczegóły żądania
- **Metoda HTTP**: `DELETE`
- **Struktura URL**: `/quizzes/{quiz_id}`
- **Parametry**:
  - **Wymagane**:
    - `quiz_id` (w ścieżce): `int` - Unikalny identyfikator quizu do usunięcia.
  - **Opcjonalne**: Brak.
- **Request Body**: Brak.

## 3. Wykorzystywane typy
Dla tego punktu końcowego nie są wymagane żadne specyficzne schematy Pydantic (DTO), ponieważ żądanie nie zawiera ciała, a udana odpowiedź nie zwraca żadnej treści.

## 4. Szczegóły odpowiedzi
- **Odpowiedź sukcesu**:
  - **Kod stanu**: `204 No Content`
  - **Treść**: Brak.
- **Odpowiedzi błędów**:
  - **Kod stanu**: `401 Unauthorized` - Gdy token uwierzytelniający jest nieprawidłowy lub go brakuje.
  - **Kod stanu**: `403 Forbidden` - Gdy uwierzytelniony użytkownik nie ma roli 'admin'.
  - **Kod stanu**: `404 Not Found` - Gdy quiz o podanym `quiz_id` nie istnieje.
  - **Kod stanu**: `500 Internal Server Error` - W przypadku ogólnego błędu serwera (np. błąd bazy danych).

## 5. Przepływ danych
1.  Żądanie `DELETE` trafia do routera API pod adresem `/quizzes/{quiz_id}`.
2.  FastAPI waliduje typ parametru ścieżki `quiz_id` (musi być to liczba całkowita).
3.  Uruchamiana jest zależność bezpieczeństwa, która weryfikuje token JWT użytkownika i sprawdza, czy posiada on rolę `admin`.
4.  Jeśli uwierzytelnianie lub autoryzacja nie powiedzie się, proces jest przerywany i zwracany jest odpowiedni błąd (`401` lub `403`).
5.  Router wywołuje funkcję CRUD (`crud.quiz.get`), aby pobrać obiekt quizu z bazy danych na podstawie `quiz_id`.
6.  Jeśli quiz nie zostanie znaleziony, funkcja zgłasza `HTTPException` ze statusem `404 Not Found`.
7.  Jeśli quiz istnieje, wywoływana jest funkcja `crud.quiz.remove` z `quiz_id`.
8.  Warstwa ORM (SQLAlchemy) wykonuje operację `DELETE` na tabeli `quizzes`.
9.  Baza danych, dzięki zdefiniowanym więzom `ON DELETE CASCADE`, automatycznie usuwa wszystkie powiązane rekordy w tabelach `questions`, `answers` i `results`.
10. Po pomyślnym usunięciu, API zwraca odpowiedź ze statusem `204 No Content`.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Wymagany jest ważny token JWT, który musi być przekazany w nagłówku żądania.
- **Autoryzacja**: Punkt końcowy musi być chroniony przez zależność, która sprawdza, czy rola użytkownika w tokenie to `admin`. Należy uniemożliwić dostęp użytkownikom z rolą `student` oraz użytkownikom nieuwierzytelnionym.
- **Walidacja danych wejściowych**: FastAPI zapewnia podstawową walidację typu dla `quiz_id`. Logika aplikacji musi zweryfikować istnienie zasobu przed próbą jego usunięcia, aby uniknąć niepotrzebnych operacji i zapewnić poprawną obsługę błędów.

## 7. Obsługa błędów
- **Quiz nie istnieje**: Sprawdź istnienie quizu za pomocą `crud.quiz.get()`. Jeśli zwróci `None`, zgłoś `HTTPException(status_code=404, detail="Quiz not found")`.
- **Brak uprawnień**: Zależność bezpieczeństwa powinna zgłosić `HTTPException(status_code=403, detail="The user does not have enough privileges")` jeśli rola nie jest `admin`.
- **Błędy bazy danych**: Wszelkie inne wyjątki z warstwy bazy danych powinny być przechwytywane i logowane, a do klienta powinna zostać zwrócona generyczna odpowiedź `500 Internal Server Error`.

## 8. Rozważania dotyczące wydajności
- Operacja usuwania pojedynczego rekordu jest zazwyczaj bardzo szybka.
- Potencjalnym wąskim gardłem może być kaskadowe usuwanie, jeśli quiz zawiera bardzo dużą liczbę pytań i wyników. Jest to jednak oczekiwane zachowanie i akceptowalny kompromis dla zapewnienia spójności danych. Na obecnym etapie nie są wymagane żadne specjalne optymalizacje.

## 9. Etapy wdrożenia
1.  **Modyfikacja warstwy CRUD**:
    -   W pliku `backend/app/crud/base.py`, upewnij się, że istnieje generyczna metoda `remove` lub zaimplementuj ją. Powinna ona przyjmować `db: Session` oraz `id: int`, znajdować obiekt po ID, usuwać go za pomocą `db.delete(obj)` i zatwierdzać transakcję `db.commit()`.
    -   `def remove(self, db: Session, *, id: int) -> ModelType:`
    -   `   obj = db.query(self.model).get(id)`
    -   `   db.delete(obj)`
    -   `   db.commit()`
    -   `   return obj`

2.  **Implementacja punktu końcowego w routerze**:
    -   W pliku `backend/app/routers/quizzes.py` dodaj nową operację ścieżki.
    -   Użyj dekoratora `@router.delete("/{quiz_id}", status_code=204)`.
    -   Zdefiniuj funkcję `delete_quiz` przyjmującą `quiz_id: int`, `db: Session = Depends(get_db)` oraz `current_user: models.User = Depends(deps.get_current_active_admin)`.
    -   Wewnątrz funkcji:
        1.  Wywołaj `quiz = crud.quiz.get(db=db, id=quiz_id)`, aby sprawdzić, czy quiz istnieje.
        2.  Jeśli `quiz` jest `None`, zgłoś `HTTPException(status_code=404, detail="Quiz not found")`.
        3.  Wywołaj `crud.quiz.remove(db=db, id=quiz_id)`.
        4.  Zwróć `Response(status_code=status.HTTP_204_NO_CONTENT)`.

3.  **Dodanie testów jednostkowych/integracyjnych**:
    -   W katalogu `backend/app/tests/api/` utwórz lub zaktualizuj plik testowy dla quizów.
    -   Napisz test sprawdzający, czy administrator może pomyślnie usunąć quiz (oczekiwany status `204`).
    -   Napisz test sprawdzający, czy próba usunięcia nieistniejącego quizu zwraca błąd `404`.
    -   Napisz test sprawdzający, czy użytkownik z rolą `student` nie może usunąć quizu (oczekiwany status `403`).
    -   Napisz test sprawdzający, czy niezalogowany użytkownik nie może usunąć quizu (oczekiwany status `401`). 