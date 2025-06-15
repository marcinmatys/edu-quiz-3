# Plan implementacji widoku: Rozwiązywanie i Podsumowanie Quizu

## 1. Przegląd
Celem jest stworzenie interfejsu dla ucznia do rozwiązywania quizu i przeglądania jego wyników. Widok prowadzi użytkownika przez serię pytań, dostarczając natychmiastowej informacji zwrotnej po każdej odpowiedzi. Po ukończeniu quizu, prezentowane jest podsumowanie z wynikiem, który jest zapisywany w systemie. Całość składa się z dwóch powiązanych ze sobą ekranów: strony rozwiązywania quizu i strony podsumowania.

## 2. Routing widoku
- **Widok rozwiązywania quizu**: Dostępny pod dynamiczną ścieżką `/student/quiz/:quizId`.
- **Widok podsumowania quizu**: Dostępny pod ścieżką `/student/quiz/:quizId/summary`.

## 3. Struktura komponentów
Komponenty zostaną zorganizowane w logiczną hierarchię, gdzie komponent-kontener (`QuizTakePage`) zarządza logiką i stanem, a komponenty podrzędne są odpowiedzialne za prezentację.

```
/student/quiz/:quizId
└── QuizTakePage
    ├── (useQuizEngine - custom hook)
    ├── QuizDisplay
    │   ├── QuizProgressBar
    │   ├── QuestionStatement
    │   └── AnswerList
    │       └── AnswerOption (mapowany)
    ├── FeedbackDisplay
    └── QuizControls

/student/quiz/:quizId/summary
└── QuizSummaryPage
    └── SummaryCard
```

## 4. Szczegóły komponentów

### `QuizTakePage` (Kontener)
- **Opis**: Główny komponent strony, orkiestrujący cały proces rozwiązywania quizu. Wykorzystuje custom hook `useQuizEngine` do zarządzania stanem, logiką i komunikacją z API. Renderuje komponenty UI w zależności od aktualnego stanu quizu (ładowanie, pytanie, informacja zwrotna).
- **Główne elementy**: `div` jako kontener dla `QuizDisplay`, `FeedbackDisplay` i `QuizControls`. Renderuje komponent `Loader` podczas ładowania danych quizu.
- **Obsługiwane interakcje**: Brak bezpośrednich interakcji. Przekazuje funkcje obsługi zdarzeń z hooka do komponentów podrzędnych.
- **Typy**: `QuizReadDetailStudentDto`
- **Propsy**: Brak. Pobiera `quizId` z parametrów URL.

### `QuizDisplay`
- **Opis**: Wyświetla aktualne pytanie wraz z opcjami odpowiedzi i paskiem postępu.
- **Główne elementy**: `Card` (shadcn/ui) zawierający `QuizProgressBar`, `QuestionStatement` i `AnswerList`.
- **Obsługiwane interakcje**: Brak.
- **Typy**: `QuestionReadStudentDto`, `AnswerStateViewModel[]`
- **Propsy**:
    - `question: QuestionReadStudentDto` - obiekt aktualnego pytania.
    - `answerStates: AnswerStateViewModel[]` - stan wizualny odpowiedzi.
    - `progress: { current: number, total: number }` - dane do paska postępu.
    - `onAnswerSelect: (answerId: number) => void` - funkcja wywoływana po wybraniu odpowiedzi.
    - `isAnswerChecked: boolean` - flaga informująca, czy odpowiedź na bieżące pytanie została już sprawdzona.

### `AnswerOption`
- **Opis**: Interaktywny przycisk reprezentujący pojedynczą odpowiedź. Jego wygląd (kolor tła, ikona) zmienia się w zależności od statusu.
- **Główne elementy**: `Button` (shadcn/ui).
- **Obsługiwane interakcje**: `onClick`.
- **Warunki walidacji**: Przycisk jest wyłączony (`disabled`), jeśli odpowiedź na bieżące pytanie została już sprawdzona.
- **Typy**: `AnswerStateViewModel`
- **Propsy**:
    - `answer: AnswerStateViewModel` - dane odpowiedzi wraz z jej statusem.
    - `onClick: (answerId: number) => void` - funkcja zwrotna z ID odpowiedzi.
    - `disabled: boolean` - do blokowania przycisku.

### `FeedbackDisplay`
- **Opis**: Komponent wyświetlający wyjaśnienie od AI po sprawdzeniu odpowiedzi. Jest widoczny tylko wtedy, gdy informacja zwrotna jest dostępna.
- **Główne elementy**: `div` z tekstem wyjaśnienia, ostylowany jako `Alert` (shadcn/ui).
- **Obsługiwane interakcje**: Brak.
- **Propsy**:
    - `feedback: string | null` - treść wyjaśnienia.

### `QuizControls`
- **Opis**: Zawiera przyciski nawigacyjne, takie jak "Następne pytanie" lub "Zakończ quiz".
- **Główne elementy**: `Button` (shadcn/ui).
- **Obsługiwane interakcje**: `onClick`.
- **Warunki walidacji**: Przycisk jest wyłączony (`disabled`), dopóki użytkownik nie wybierze odpowiedzi i nie zostanie ona sprawdzona przez serwer. Tekst na przycisku zmienia się na "Zakończ quiz" przy ostatnim pytaniu.
- **Propsy**:
    - `onNext: () => void` - funkcja wywoływana po kliknięciu.
    - `isNextDisabled: boolean` - flaga do wyłączania przycisku.
    - `isLastQuestion: boolean` - flaga informująca, czy to ostatnie pytanie.

### `QuizSummaryPage` (Kontener)
- **Opis**: Strona wyświetlająca podsumowanie quizu. Pobiera wynik z `location.state` przekazanego przez `react-router-dom`.
- **Główne elementy**: `div` jako kontener dla `SummaryCard`.
- **Obsługiwane interakcje**: Brak.
- **Warunki walidacji**: Jeśli `location.state` nie zawiera wyników (np. przy bezpośrednim wejściu na URL), użytkownik jest przekierowywany do listy quizów.
- **Propsy**: Brak.

### `SummaryCard`
- **Opis**: Prezentuje finalny wynik w formacie "X/Y" i oferuje możliwość powrotu do listy quizów.
- **Główne elementy**: `Card` (shadcn/ui) z tekstem wyniku i przyciskiem `Button`.
- **Obsługiwane interakcje**: `onClick` na przycisku powrotu.
- **Propsy**:
    - `score: number` - zdobyta liczba punktów.
    - `maxScore: number` - maksymalna liczba punktów.
    - `onReturn: () => void` - funkcja nawigująca do listy quizów.

## 5. Typy
Definicje typów w TypeScript, które będą używane w komponentach i logice.

```typescript
// --- DTOs (Data Transfer Objects) ---

// Odpowiedź serwera dla GET /quizzes/{quiz_id} (dla studenta)
export interface AnswerReadStudentDto {
  id: number;
  text: string;
}

export interface QuestionReadStudentDto {
  id: number;
  text: string;
  answers: AnswerReadStudentDto[];
}

export interface QuizReadDetailStudentDto {
  id: number;
  title: string;
  description: string;
  questions: QuestionReadStudentDto[];
}

// Ciało żądania dla POST /quizzes/{quiz_id}/check-answer
export interface AnswerCheckRequestDto {
  question_id: number;
  answer_id: number;
}

// Odpowiedź serwera dla POST /quizzes/{quiz_id}/check-answer
export interface AnswerCheckResponseDto {
  is_correct: boolean;
  correct_answer_id: number;
  explanation: string;
}

// Ciało żądania dla POST /quizzes/{quiz_id}/results
export interface ResultCreateDto {
  score: number;
  max_score: number;
}

// --- ViewModels ---

// Typ określający status wizualny odpowiedzi w UI
export type AnswerStatus = 'default' | 'selected' | 'correct' | 'incorrect';

// Model widoku dla pojedynczej odpowiedzi
export interface AnswerStateViewModel {
  id: number;
  text: string;
  status: AnswerStatus;
}
```

## 6. Zarządzanie stanem
Logika i stan komponentu zostaną scentralizowane w custom hooku `useQuizEngine` w celu separacji logiki od prezentacji.

### `useQuizEngine(quizId: string)`
- **Cel**: Hermetyzacja całej logiki biznesowej związanej z rozwiązywaniem quizu.
- **Stan wewnętrzny**:
    - `quizQuery` (`useQuery`): Stan pobierania danych o quizie.
    - `checkAnswerMutation` (`useMutation`): Stan sprawdzania odpowiedzi.
    - `submitResultMutation` (`useMutation`): Stan zapisu wyniku.
    - `currentQuestionIndex: number`: Indeks bieżącego pytania w tablicy pytań.
    - `score: number`: Liczba poprawnych odpowiedzi.
    - `checkedAnswerInfo: AnswerCheckResponseDto | null`: Przechowuje wynik ostatniego sprawdzenia odpowiedzi, aby sterować stanem UI.
- **Eksportowane wartości i funkcje**:
    - `quizData`, `isLoadingQuiz`: Dane quizu i stan ładowania.
    - `currentQuestion`: Obiekt bieżącego pytania.
    - `answerStates`: Wyliczana na bieżąco tablica `AnswerStateViewModel[]` dla bieżącego pytania.
    - `feedback`: Wyjaśnienie AI do wyświetlenia.
    - `isSubmitting`: Flaga łącząca stany `isPending` z mutacji.
    - `isFinished`: Flaga informująca o zakończeniu quizu.
    - `progress`: Obiekt `{ current: number, total: number }`.
    - `handleAnswerSelect(answerId: number)`: Funkcja do sprawdzania odpowiedzi.
    - `handleNext()`: Funkcja do przechodzenia do następnego pytania lub zakończenia quizu.

Stan na stronie podsumowania (`QuizSummaryPage`) będzie przekazywany przez `react-router-dom` za pomocą `navigate('/path', { state: { ... } })`.

## 7. Integracja API
Integracja z backendem będzie realizowana przy użyciu `TanStack Query`.

- **Pobieranie danych quizu**:
    - **Endpoint**: `GET /api/v1/quizzes/{quiz_id}`
    - **Hook**: `useQuery`
    - **Typ odpowiedzi**: `QuizReadDetailStudentDto`
- **Sprawdzanie odpowiedzi**:
    - **Endpoint**: `POST /api/v1/quizzes/{quiz_id}/check-answer`
    - **Hook**: `useMutation`
    - **Typ żądania**: `AnswerCheckRequestDto`
    - **Typ odpowiedzi**: `AnswerCheckResponseDto`
- **Zapisywanie wyniku**:
    - **Endpoint**: `POST /api/v1/quizzes/{quiz_id}/results`
    - **Hook**: `useMutation`
    - **Typ żądania**: `ResultCreateDto`
    - **Typ odpowiedzi**: `ResultRead`

## 8. Interakcje użytkownika
1.  Uczeń wchodzi na stronę `/student/quiz/{quizId}`. Aplikacja wyświetla ekran ładowania i pobiera dane quizu.
2.  Po załadowaniu, wyświetlane jest pierwsze pytanie i 4 możliwe odpowiedzi. Przycisk "Następne pytanie" jest nieaktywny.
3.  Uczeń klika jedną z odpowiedzi.
4.  Wszystkie opcje odpowiedzi stają się nieaktywne. Wybrana opcja jest oznaczana jako "wybrana".
5.  Wysyłane jest żądanie do API w celu sprawdzenia odpowiedzi.
6.  Po otrzymaniu odpowiedzi z API:
    - Wybrana opcja jest oznaczana jako "poprawna" lub "niepoprawna".
    - W przypadku błędnej odpowiedzi, poprawna opcja również jest wyróżniana.
    - Pod odpowiedziami pojawia się wyjaśnienie od AI.
    - Przycisk "Następne pytanie" staje się aktywny.
7.  Uczeń klika "Następne pytanie", co powoduje wyświetlenie kolejnego pytania i zresetowanie stanu odpowiedzi.
8.  Proces powtarza się dla wszystkich pytań. Przy ostatnim pytaniu przycisk zmienia tekst na "Zakończ quiz".
9.  Po kliknięciu "Zakończ quiz", aplikacja wysyła wynik do API.
10. Po pomyślnym zapisie wyniku, uczeń jest przekierowywany na stronę podsumowania (`/student/quiz/{quizId}/summary`).
11. Strona podsumowania wyświetla wynik (np. "8/10") oraz przycisk "Wróć do listy quizów".

## 9. Warunki i walidacja
- **Blokada ponownej odpowiedzi**: Po wybraniu odpowiedzi i wysłaniu jej do weryfikacji, wszystkie przyciski odpowiedzi dla bieżącego pytania muszą zostać zablokowane, aby zapobiec wielokrotnemu odpowiadaniu.
- **Wymuszenie sekwencji**: Przycisk "Następne pytanie" musi być nieaktywny do momentu, aż odpowiedź na bieżące pytanie zostanie sprawdzona przez API.
- **Dostęp do podsumowania**: Strona podsumowania powinna być dostępna tylko po ukończeniu quizu. Bezpośrednie wejście na jej URL (bez stanu z wynikiem) powinno skutkować przekierowaniem.

## 10. Obsługa błędów
- **Błąd pobierania quizu**: Jeśli `useQuery` dla danych quizu zwróci błąd, na stronie zostanie wyświetlony komunikat o błędzie z możliwością ponownego załadowania.
- **Błąd sprawdzania odpowiedzi**: Jeśli mutacja `checkAnswer` zakończy się błędem, zostanie wyświetlony komunikat typu "toast" (np. przy użyciu `sonner`) informujący o problemie, a interfejs pozwoli użytkownikowi spróbować ponownie wybrać odpowiedź.
- **Błąd zapisu wyniku**: Jeśli mutacja `submitResult` nie powiedzie się, użytkownik zobaczy toast z błędem i pozostanie na ostatnim pytaniu, z aktywnym przyciskiem "Zakończ quiz", aby mógł ponowić próbę.
- **Brak danych na stronie podsumowania**: `QuizSummaryPage` sprawdzi, czy `location.state` zawiera wymagane dane. Jeśli nie, przekieruje użytkownika na stronę listy quizów (`/student/quizzes`).

## 11. Kroki implementacji
1.  **Konfiguracja routingu**: Dodanie nowych ścieżek (`/student/quiz/:quizId` i `/student/quiz/:quizId/summary`) w głównym pliku routingu aplikacji.
2.  **Definicje typów**: Stworzenie pliku `types/quiz.ts` (lub w odpowiednim miejscu) i zdefiniowanie w nim wszystkich interfejsów DTO i ViewModel.
3.  **Implementacja `useQuizEngine`**: Stworzenie pliku `hooks/useQuizEngine.ts`. Zaimplementowanie w nim całej logiki: `useQuery` do pobierania quizu, `useMutation` do sprawdzania odpowiedzi i zapisu wyniku, oraz zarządzanie stanem lokalnym (`currentQuestionIndex`, `score` itp.).
4.  **Budowa `QuizTakePage`**: Stworzenie komponentu, który użyje hooka `useQuizEngine` i będzie renderować komponenty podrzędne na podstawie zwracanego przez niego stanu.
5.  **Stworzenie komponentów prezentacyjnych**: Implementacja komponentów: `QuizDisplay`, `QuizProgressBar`, `QuestionStatement`, `AnswerList`, `AnswerOption`, `FeedbackDisplay` i `QuizControls`. Przekazanie do nich propsów i funkcji obsługi zdarzeń.
6.  **Styling**: Ostylowanie wszystkich komponentów za pomocą Tailwind CSS i komponentów `shadcn/ui`. Zwrócenie szczególnej uwagi na dynamiczne style przycisku `AnswerOption` w zależności od jego statusu.
7.  **Budowa `QuizSummaryPage`**: Stworzenie strony podsumowania, która odczytuje dane z `location.state` i renderuje `SummaryCard`. Implementacja logiki przekierowania w przypadku braku danych.
8.  **Implementacja obsługi błędów**: Zintegrowanie biblioteki `sonner` do wyświetlania toastów w przypadku błędów API. Dodanie komunikatów o błędach na stronie.
9.  **Testowanie**: Manualne przetestowanie całego przepływu: ładowanie, odpowiadanie, obsługa błędów, ukończenie quizu, podsumowanie i nawigacja. 