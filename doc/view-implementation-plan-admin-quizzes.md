# Plan implementacji widoku: Panel Zarządzania Quizami Administratora

## 1. Przegląd
Widok ten stanowi centrum zarządzania quizami dla administratora. Umożliwia on przeglądanie wszystkich istniejących quizów (zarówno w wersji roboczej, jak i opublikowanych), tworzenie nowych quizów z pomocą AI, edycję, publikację oraz usuwanie quizów. Widok ten jest kluczowy dla cyklu życia quizu w aplikacji, od jego powstania aż po udostępnienie go uczniom.

## 2. Routing widoku
Widok Panelu Administratora powinien być dostępny pod chronioną ścieżką, dedykowaną dla zalogowanych użytkowników z rolą administratora.
- **Ścieżka**: `/admin/quizzes`

## 3. Struktura komponentów
Hierarchia komponentów zostanie zorganizowana w sposób modułowy, aby zapewnić reużywalność i czytelność kodu.

```
/admin/quizzes -> AdminQuizzesPage
    ├── QuizListToolbar
    │   ├── FilterDropdown (filtrowanie wg statusu)
    │   └── CreateQuizButton (otwiera CreateQuizDialog)
    ├── QuizList
    │   └── QuizListItem (mapowany, implementowany jako shadcn/ui Card)
    │       ├── QuizDetails (tytuł, poziom, status)
    │       └── ActionButtons (Edytuj, Usuń)
    └── QuizEditor (renderowany warunkowo lub na osobnej podstronie, np. /admin/quizzes/edit)
        ├── QuizEditorForm (zarządza całym stanem formularza edycji)
        │   ├── QuizMetadataInputs (pola na tytuł, poziom)
        │   └── QuestionsList
        │       └── QuestionEditor (mapowany)
        │           └── ... (pola do edycji pytania i odpowiedzi)
        └── EditorFooter
            ├── SaveButton (zapisz jako wersję roboczą)
            ├── PublishButton (publikuj)
            └── CancelButton (anuluj)
```
Komponent `CreateQuizDialog` będzie modalnym oknem dialogowym (`shadcn/ui Dialog`) do tworzenia nowego quizu.

## 4. Szczegóły komponentów

### `AdminQuizzesPage`
- **Opis**: Główny komponent-kontener strony. Zarządza stanem (lista quizów, tryb widoku), obsługuje logikę pobierania i modyfikacji danych za pomocą customowego hooka `useAdminQuizzes`.
- **Główne elementy**: `QuizListToolbar`, `QuizList`, `QuizEditor`.
- **Obsługiwane interakcje**: Przełączanie między widokiem listy a edytorem, inicjowanie tworzenia/edycji/usuwania quizu.
- **Typy**: `QuizListItemVM`, `QuizEditorVM`.
- **Propsy**: Brak.

### `QuizList`
- **Opis**: Komponent prezentacyjny wyświetlający listę quizów w formie siatki kart. Każda karta (`QuizListItem`) reprezentuje pojedynczy quiz i zawiera jego kluczowe informacje oraz przyciski akcji.
- **Główne elementy**: `div` (jako kontener siatki), `Card` (dla każdego `QuizListItem`), `Badge` (do oznaczenia statusu), `Button` (dla akcji), `Tooltip` (dla przycisków akcji).
- **Obsługiwane interakcje**: Kliknięcie przycisków "Edytuj" i "Usuń".
- **Typy**: `QuizListItemVM[]`.
- **Propsy**:
  - `quizzes: QuizListItemVM[]`
  - `onEdit: (quizId: number) => void`
  - `onDelete: (quizId: number) => void`

### `CreateQuizDialog`
- **Opis**: Modalne okno dialogowe z formularzem do generowania nowego quizu przez AI.
- **Główne elementy**: `Dialog`, `Form`, `Input`, `Select`, `Button`.
- **Obsługiwane interakcje**: Wprowadzanie danych, zatwierdzenie formularza, anulowanie.
- **Warunki walidacji**:
  - `Temat`: Pole wymagane, nie może być puste.
  - `Liczba pytań`: Pole wymagane, musi być liczbą całkowitą dodatnią (np. > 0).
  - `Poziom zaawansowania`: Pole wymagane, musi być wybraną opcją.
- **Typy**: `CreateQuizRequestDto`.
- **Propsy**:
  - `isOpen: boolean`
  - `onClose: () => void`
  - `onSubmit: (data: CreateQuizRequestDto) => void`

### `QuizEditor`
- **Opis**: Komponent do edycji istniejącego quizu lub weryfikacji nowo wygenerowanego. Zarządza stanem formularza edytowanego quizu.
- **Główne elementy**: `Form`, `Input` (dla tytułu), `Select` (dla poziomu), `QuestionEditor` (dla pytań).
- **Obsługiwane interakcje**: Modyfikacja tytułu, poziomu, treści pytań i odpowiedzi, zmiana poprawnej odpowiedzi, dodawanie/usuwanie pytań, zapisanie, opublikowanie lub anulowanie edycji.
- **Warunki walidacji**:
  - `Tytuł`: Pole wymagane.
  - `Pytania`: Każde pytanie musi mieć treść.
  - `Odpowiedzi`: Każda odpowiedź musi mieć treść. Każde pytanie musi mieć dokładnie jedną poprawną odpowiedź.
- **Typy**: `QuizEditorVM`.
- **Propsy**:
  - `quiz: QuizEditorVM`
  - `onSave: (quizData: QuizEditorVM) => void`
  - `onPublish: (quizData: QuizEditorVM) => void`
  - `onCancel: () => void`

## 5. Typy

### DTO (Data Transfer Objects) - zgodne z API
```typescript
// GET /quizzes
interface QuizListItemDto {
  id: number;
  title: string;
  status: 'published' | 'draft';
  level_id: number;
  question_count: number;
  updated_at: string;
}

// PUT /quizzes/{id} Request Body
interface QuizUpdateDto {
  title?: string;
  status?: 'published' | 'draft';
  level_id?: number;
  questions?: {
    id?: number; // Brak ID dla nowego pytania
    text: string;
    answers: {
      id?: number; // Brak ID dla nowej odpowiedzi
      text: string;
      is_correct: boolean;
    }[];
  }[];
}

// POST /quizzes/generate (hipotetyczny endpoint)
interface CreateQuizRequestDto {
  topic: string;
  question_count: number;
  level_id: number;
}
```

### ViewModel (typy na potrzeby widoku)
```typescript
// Typ dla elementu na liście quizów
interface QuizListItemVM extends Omit<QuizListItemDto, 'level_id'> {
  level: string; // np. "Klasa IV" zamiast ID
}

// Typ dla stanu edytora quizów
// Może być tożsamy z QuizUpdateDto, ale z wymaganymi wszystkimi polami
// na potrzeby formularza
interface AnswerVM {
  id?: number;
  uiId: string; // Unikalne ID na potrzeby UI (np. dla kluczy w listach Reacta)
  text: string;
  is_correct: boolean;
}

interface QuestionVM {
  id?: number;
  uiId: string;
  text: string;
  answers: AnswerVM[];
}

interface QuizEditorVM {
  id?: number;
  title: string;
  level_id: number;
  questions: QuestionVM[];
}
```

## 6. Zarządzanie stanem
Stan będzie zarządzany głównie za pomocą hooka `useState` w poszczególnych komponentach oraz jednego nadrzędnego, customowego hooka `useAdminQuizzes`, który będzie hermetyzował logikę biznesową i komunikację z API.

### `useAdminQuizzes`
- **Cel**: Centralizacja logiki pobierania, tworzenia, aktualizacji i usuwania quizów.
- **Zwracane wartości**:
  - `quizzes: QuizListItemVM[]`: Lista quizów.
  - `currentQuiz: QuizEditorVM | null`: Quiz w trakcie edycji.
  - `isLoading: boolean`: Status ładowania danych.
  - `error: Error | null`: Ewentualny błąd z API.
  - `actions`: Obiekt z funkcjami:
    - `fetchQuizzes(filters: { status?: string })`
    - `selectQuizForEdit(quizId: number)`
    - `createNewQuiz(data: CreateQuizRequestDto)`
    - `saveQuiz(quizData: QuizEditorVM)`
    - `publishQuiz(quizData: QuizEditorVM)`
    - `deleteQuiz(quizId: number)`
    - `clearSelection()`

## 7. Integracja API

- **Pobieranie listy quizów**: `GET /quizzes`
  - Wywoływane przy pierwszym renderowaniu `AdminQuizzesPage` oraz po zmianie filtrów.
  - Odpowiedź typu `QuizListItemDto[]` jest mapowana na `QuizListItemVM[]`.
- **Aktualizacja quizu (zapis/publikacja)**: `PUT /quizzes/{quiz_id}`
  - Wywoływane przez `saveQuiz` i `publishQuiz`.
  - Ciało żądania (`QuizUpdateDto`) jest budowane na podstawie stanu `QuizEditorVM`. Status jest ustawiany odpowiednio na `'draft'` lub `'published'`.
- **Usuwanie quizu**: `DELETE /quizzes/{quiz_id}`
  - Wywoływane przez `deleteQuiz` po potwierdzeniu przez użytkownika.
- **Tworzenie quizu (AI)**: `POST /quizzes/generate` (hipotetyczny endpoint)
  - Wywoływane przez `createNewQuiz` z danymi z `CreateQuizDialog`.
  - Po otrzymaniu odpowiedzi (wygenerowany quiz) widok przechodzi w tryb edycji/weryfikacji.

## 8. Interakcje użytkownika

- **Wyświetlanie listy**: Domyślnie użytkownik widzi listę wszystkich quizów.
- **Filtrowanie**: Użytkownik może filtrować listę po statusie ('roboczy'/'opublikowany').
- **Tworzenie quizu**: Kliknięcie "Stwórz nowy quiz" otwiera dialog, gdzie użytkownik podaje temat, liczbę pytań i poziom. Po zatwierdzeniu wyświetlany jest loader, a następnie edytor z wygenerowanym quizem.
- **Edycja quizu**: Kliknięcie "Edytuj" przy quizie na liście otwiera widok `QuizEditor` z załadowanymi danymi tego quizu.
- **Zapisywanie zmian**: W edytorze użytkownik może modyfikować dane. "Zapisz" wysyła `PUT` i wraca do listy. "Publikuj" wysyła `PUT` ze statusem `published` i wraca do listy.
- **Usuwanie quizu**: Kliknięcie "Usuń" wymaga dodatkowego potwierdzenia (np. w `AlertDialog`) przed wysłaniem `DELETE`.

## 9. Warunki i walidacja

- **Formularz tworzenia quizu**: Walidacja po stronie klienta (z użyciem biblioteki jak `zod` zintegrowanej z `react-hook-form`) sprawdzi, czy temat nie jest pusty, liczba pytań jest poprawną liczbą dodatnią, a poziom jest wybrany. Przycisk "Generuj" jest nieaktywny do czasu spełnienia warunków.
- **Formularz edytora quizu**:
  - Tytuł nie może być pusty.
  - Tekst pytania i odpowiedzi nie mogą być puste.
  - Każde pytanie musi mieć zaznaczoną jedną, i tylko jedną, poprawną odpowiedź.
  - Przyciski "Zapisz" i "Opublikuj" są nieaktywne, jeśli formularz jest w stanie niepoprawnym.

## 10. Obsługa błędów

- **Błędy API**: Wszelkie błędy sieciowe lub odpowiedzi serwera z kodem 4xx/5xx będą przechwytywane przez `useAdminQuizzes`. Komunikat o błędzie (np. "Nie udało się pobrać quizów") będzie wyświetlany użytkownikowi za pomocą komponentu `Alert` lub `Toast` z `shadcn/ui`.
- **Błędy walidacji (API)**: Jeśli API zwróci błąd `422 Unprocessable Entity`, odpowiednie komunikaty o błędach zostaną wyświetlone przy polach formularza.
- **Przypadki brzegowe**:
  - **Pusta lista quizów**: Wyświetlony zostanie komunikat zachęcający do stworzenia pierwszego quizu.
  - **Próba edycji opublikowanego quizu**: Przycisk "Edytuj" może być wyszarzony lub jego funkcjonalność ograniczona (zależnie od wymagań biznesowych, które należałoby doprecyzować). Na ten moment, zgodnie z user stories, edytujemy tylko wersje robocze.

## 11. Kroki implementacji

1.  **Stworzenie struktury plików**: Utworzenie folderów i plików dla komponentów: `AdminQuizzesPage`, `QuizList`, `QuizEditor` itd. w katalogu `frontend/src/components/admin`.
2.  **Implementacja typów**: Zdefiniowanie wszystkich typów DTO i ViewModel w pliku `frontend/src/types/quiz.ts`.
3.  **Implementacja hooka `useAdminQuizzes`**: Stworzenie logiki do komunikacji z API, bez UI. Mockowanie API na początkowym etapie (`msw` lub podobne) może przyspieszyć pracę.
4.  **Implementacja `AdminQuizzesPage` i `QuizList`**: Zbudowanie widoku listy quizów, integracja z `useAdminQuizzes` w celu pobrania i wyświetlenia danych.
5.  **Implementacja `CreateQuizDialog`**: Stworzenie formularza do generowania quizu wraz z walidacją po stronie klienta.
6.  **Implementacja `QuizEditor`**: Zbudowanie złożonego formularza edycji quizu. Należy zwrócić szczególną uwagę na zarządzanie stanem listy pytań i odpowiedzi (np. za pomocą `useFieldArray` z `react-hook-form`).
7.  **Integracja komponentów**: Połączenie wszystkich komponentów w spójną całość na `AdminQuizzesPage`, implementacja logiki przełączania widoków (lista/edycja).
8.  **Obsługa usuwania i potwierdzeń**: Dodanie `AlertDialog` do potwierdzania operacji usuwania.
9.  **Obsługa stanu ładowania i błędów**: Implementacja wizualnych wskaźników (np. `Spinner`) podczas ładowania danych oraz wyświetlanie komunikatów o błędach (`Toast`/`Alert`).
10. **Stylowanie i dopracowanie UI**: Finalne dopracowanie wyglądu za pomocą Tailwind CSS i komponentów `shadcn/ui`, zapewnienie responsywności.
11. **Testowanie**: Przeprowadzenie manualnych testów wszystkich ścieżek użytkownika opisanych w historyjkach. 