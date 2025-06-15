# Plan implementacji widoku: Panel Ucznia

## 1. Przegląd
Widok Panelu Ucznia jest głównym ekranem dla zalogowanego ucznia. Jego celem jest wyświetlenie listy wszystkich dostępnych (opublikowanych) quizów, które uczeń może rozwiązać. Widok umożliwia sortowanie listy i zapewnia kluczowe informacje o każdym quizie, takie jak tytuł, poziom trudności, liczba pytań oraz ostatni uzyskany wynik, motywując do nauki i poprawy.

## 2. Routing widoku
Widok będzie dostępny pod chronioną ścieżką, dedykowaną dla zalogowanych użytkowników z rolą ucznia:
- **Ścieżka:** `/student/quizzes`

## 3. Struktura komponentów
Hierarchia komponentów zostanie zorganizowana w celu oddzielenia odpowiedzialności za pobieranie danych, zarządzanie stanem i renderowanie UI.

/student/dashboard -> StudentDashboard (jest już utworzone, wymaga dopracowania)
    └── /student/quizzes -> StudentQuizzesPage
          ├── QuizListControls (sortowanie, filtracja)
          └── QuizList
                ├── QuizCard (mapowany)
                └── EmptyStateMessage (gdy brak quizów)



- **`StudentQuizzesPage`**: Główny komponent strony, odpowiedzialny za layout oraz orkiestrację pobierania danych i obsługi stanu (ładowanie, błędy) przy użyciu hooka `useStudentQuizzes`.
- **`QuizListControls`**: Komponent zawierający kontrolki do interakcji z listą, np. `Select` do zmiany kryterium sortowania.
- **`QuizList`**: Komponent, który otrzymuje listę quizów i renderuje komponent `QuizCard` dla każdego elementu lub `EmptyStateMessage`, jeśli lista jest pusta.
- **`QuizCard`**: Komponent prezentujący dane pojedynczego quizu (tytuł, poziom, liczba pytań, wynik) w formie karty `shadcn/ui`. Zawiera przycisk do rozpoczęcia quizu.
- **`EmptyStateMessage`**: Komponent wyświetlany, gdy nie ma żadnych quizów do pokazania.

## 4. Szczegóły komponentów
### `StudentQuizzesPage`
- **Opis:** Kontener widoku. Inicjuje pobieranie danych, obsługuje stany ładowania i błędów na poziomie całej strony.
- **Główne elementy:** Podstawowy layout, nagłówek (`<h1>`), oraz komponenty `QuizListControls` i `QuizList`. Wyświetla globalny wskaźnik ładowania lub komunikat o błędzie.
- **Obsługiwane interakcje:** Brak bezpośrednich interakcji, deleguje je do komponentów podrzędnych.
- **Typy:** Brak bezpośrednich typów, operuje na stanie z hooka `useStudentQuizzes`.
- **Propsy:** Brak.

### `QuizListControls`
- **Opis:** Pasek narzędzi do zarządzania listą quizów.
- **Główne elementy:** Komponent `Select` z `shadcn/ui` do wyboru opcji sortowania (np. "Poziom trudności", "Tytuł").
- **Obsługiwane interakcje:** Zmiana wartości w selektorze sortowania.
- **Obsługiwana walidacja:** Brak.
- **Typy:** `SortParams { sortBy: string, order: 'asc' | 'desc' }`.
- **Propsy:**
    - `sortParams: SortParams`
    - `onSortChange: (newParams: SortParams) => void`

### `QuizList`
- **Opis:** Wyświetla siatkę lub listę quizów.
- **Główne elementy:** Warunkowe renderowanie: jeśli `isLoading` - wyświetla szkielety ładowania; jeśli `quizzes.length === 0` - wyświetla `EmptyStateMessage`; w przeciwnym razie - mapuje tablicę `quizzes` i renderuje komponenty `QuizCard`.
- **Obsługiwane interakcje:** Brak.
- **Obsługiwana walidacja:** Sprawdzenie, czy tablica z quizami jest pusta.
- **Typy:** `QuizCardViewModel[]`.
- **Propsy:**
    - `quizzes: QuizCardViewModel[]`
    - `isLoading: boolean`

### `QuizCard`
- **Opis:** Reprezentuje pojedynczy quiz na liście.
- **Główne elementy:** Komponent `Card` z `shadcn/ui` zawierający: `CardHeader` z tytułem, `CardContent` z opisem (poziom, liczba pytań) i `Badge` z ostatnim wynikiem, `CardFooter` z przyciskiem `Button` "Rozpocznij".
- **Obsługiwane interakcje:** Kliknięcie przycisku "Rozpocznij", które nawiguje do rozwiązywania quizu.
- **Obsługiwana walidacja:** Warunkowe wyświetlanie `Badge` z wynikiem (tylko jeśli `last_result` nie jest `null`).
- **Typy:** `QuizCardViewModel`.
- **Propsy:**
    - `quiz: QuizCardViewModel`

## 5. Typy
### DTO (Data Transfer Object)
Struktura danych otrzymywana bezpośrednio z API (`GET /api/v1/quizzes`).

```typescript
// Schemat odpowiedzi z API dla pojedynczego quizu na liście
interface LastResultDto {
  score: number;
  max_score: number;
}

interface QuizReadListDto {
  id: number;
  title: string;
  level_id: number;
  question_count: number;
  last_result: LastResultDto | null;
}
```

### ViewModel
Struktura danych przygotowana specjalnie na potrzeby renderowania w komponentach.

```typescript
// Model widoku dla komponentu QuizCard
interface QuizCardViewModel {
  id: number;
  title: string;
  levelDescription: string;     // np. "Klasa IV"
  questionCountText: string;    // np. "Liczba pytań: 10"
  lastResultText: string | null;  // np. "Ostatni wynik: 8/10"
  startQuizPath: string;        // np. "/student/quiz/5"
}
```

## 6. Zarządzanie stanem
Zarządzanie stanem serwera będzie realizowane za pomocą biblioteki `TanStack Query`. Lokalny stan UI (parametry sortowania) będzie zarządzany wewnątrz customowego hooka.

- **Custom Hook: `useStudentQuizzes`**
    - **Cel:** Abstrakcja logiki pobierania, cachowania, sortowania i transformacji danych.
    - **Zarządzany stan:**
        - `sortParams: { sortBy: string, order: 'asc' | 'desc' }` (stan lokalny UI).
        - Stan `TanStack Query`: `data`, `isLoading`, `isError`, `error`.
    - **Logika:** Hook będzie zawierał `useState` dla `sortParams`. `useQuery` będzie używał klucza zapytania zależnego od `sortParams` (np. `['studentQuizzes', sortParams]`), co zapewni automatyczne odświeżanie danych po zmianie sortowania. Hook będzie również odpowiedzialny za transformację `QuizReadListDto[]` na `QuizCardViewModel[]`.
    - **Zwracane wartości:** `{ quizzes: QuizCardViewModel[], isLoading, error, sortParams, setSortParams }`.
    

## 7. Integracja API
Integracja z backendem odbędzie się poprzez wywołanie punktu końcowego `GET /api/v1/quizzes`.

- **Endpoint:** `GET /api/v1/quizzes`
- **Metoda:** `GET`
- **Uwierzytelnienie:** Wymagany token JWT w nagłówku `Authorization`.
- **Parametry zapytania:**
    - `sort_by: string` (opcjonalny, domyślnie `level`)
    - `order: 'asc' | 'desc'` (opcjonalny, domyślnie `asc`)
- **Typ odpowiedzi ( sukces, `200 OK`):** `QuizReadListDto[]`
- **Obsługa:** Wywołanie będzie realizowane wewnątrz hooka `useStudentQuizzes` przy użyciu `TanStack Query`.

## 8. Interakcje użytkownika
- **Wyświetlenie widoku:** Uruchamia `useStudentQuizzes`, które wykonuje zapytanie do API z domyślnymi parametrami sortowania. Interfejs pokazuje stan ładowania.
- **Zmiana sortowania:** Użytkownik wybiera nową opcję w komponencie `QuizListControls`. Wywoływana jest funkcja `setSortParams` z hooka, co powoduje ponowne wykonanie zapytania do API z nowymi parametrami i odświeżenie listy.
- **Rozpoczęcie quizu:** Użytkownik klika przycisk "Rozpocznij" na `QuizCard`. Aplikacja nawiguje go do widoku rozwiązywania quizu (`/student/quiz/{id}`) za pomocą `useNavigate` z `react-router-dom`.

## 9. Warunki i walidacja
- **Dostęp do widoku:** Trasa `/student/quizzes` jest chroniona. Dostęp jest przyznawany tylko uwierzytelnionym użytkownikom z rolą `student`. Walidacja odbywa się na poziomie routera.
- **Brak quizów:** Jeśli API zwróci pustą tablicę, komponent `QuizList` wyświetli stosowny komunikat `EmptyStateMessage`.
- **Brak wyniku:** Komponent `QuizCard` sprawdza, czy `last_result` jest `null`. Jeśli tak, `Badge` z wynikiem nie jest renderowany.

## 10. Obsługa błędów
- **Błąd API:** Jeśli zapytanie do API zakończy się niepowodzeniem (np. błąd serwera 500), hook `useStudentQuizzes` ustawi stan `isError` na `true`. Komponent `StudentQuizzesPage` wyświetli wtedy globalny komunikat o błędzie, np. za pomocą komponentu `Alert` z `shadcn/ui`.
- **Błąd autoryzacji (401):** Globalna obsługa zapytań w aplikacji (np. interceptor w `axios`) powinna przechwycić ten błąd i automatycznie przekierować użytkownika na stronę logowania (`/login`).

## 11. Kroki implementacji
1.  **Stworzenie typów:** Zdefiniowanie interfejsów `QuizReadListDto` i `QuizCardViewModel` w dedykowanym pliku z typami.
2.  **Utworzenie hooka `useStudentQuizzes`:** Implementacja całej logiki zarządzania stanem, pobierania danych z API oraz transformacji DTO->ViewModel. Należy uwzględnić obsługę parametrów sortowania.
3.  **Implementacja komponentu `QuizCard`:** Stworzenie karty wyświetlającej dane z `QuizCardViewModel`, w tym warunkowe renderowanie ostatniego wyniku. Wygląd QuizCard powinien być spójny z analogiczną implementacją w widoku admina (@QuizList)
4.  **Implementacja komponentu `QuizList`:** Stworzenie komponentu, który przyjmuje listę quizów i renderuje `QuizCard` dla każdego elementu, obsługując stany ładowania i pustej listy.
5.  **Implementacja komponentu `QuizListControls`:** Stworzenie kontrolek sortowania.
6.  **Złożenie widoku `StudentQuizzesPage`:** Połączenie wszystkich komponentów w całość, wykorzystanie hooka `useStudentQuizzes` do zasilenia ich danymi i obsługi stanów `isLoading` i `error`.
7.  **Dodanie routingu:** Zarejestrowanie nowej, chronionej trasy `/student/quizzes` w głównym pliku konfiguracyjnym routera aplikacji.
8.  **Stworzenie funkcji pomocniczych:** Implementacja funkcji do mapowania `level_id` na `levelDescription` oraz formatowania tekstów.
9.  **Testowanie:** Manualne przetestowanie wszystkich interakcji, obsługi błędów i przypadków brzegowych (brak quizów, błąd API). 