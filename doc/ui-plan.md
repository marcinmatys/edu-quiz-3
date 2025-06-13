# Architektura UI dla EDU-QUIZ

## 1. Przegląd struktury UI

Architektura interfejsu użytkownika (UI) dla aplikacji EDU-QUIZ została zaprojektowana jako aplikacja jednostronicowa (SPA) z wykorzystaniem biblioteki React. Centralnym elementem jest routing oparty o role, który dzieli aplikację na dwie główne, chronione sekcje: panel administratora (`/admin`) i panel ucznia (`/student`).

Po pomyślnym zalogowaniu, użytkownik jest automatycznie przekierowywany do swojego panelu, w zależności od przypisanej roli. Zarządzanie stanem serwera, w tym pobieranie danych, buforowanie i mutacje, będzie realizowane przez `TanStack Query`, co zapewni responsywność i optymistyczne aktualizacje interfejsu. Stan globalny aplikacji, taki jak dane uwierzytelniające użytkownika, będzie zarządzany przez `React Context`.

Interfejs będzie zbudowany z reużywalnych komponentów z biblioteki `shadcn/ui` i stylizowany za pomocą `Tailwind CSS`, co zapewni spójny i nowoczesny wygląd. Kluczowe interakcje, takie jak generowanie quizu przez AI czy sprawdzanie odpowiedzi, będą obsługiwane asynchronicznie, z wyraźnym sygnalizowaniem stanu ładowania, aby zapewnić płynne doświadczenie użytkownika.

## 2. Lista widoków

### 1. Widok Logowania
-   **Ścieżka:** `/login`
-   **Główny cel:** Uwierzytelnienie użytkownika i uzyskanie tokenu JWT.
-   **Kluczowe informacje do wyświetlenia:** Formularz z polami na nazwę użytkownika i hasło, komunikaty o błędach walidacji lub logowania.
-   **Kluczowe komponenty:** `Card`, `Form`, `Input`, `Button`, `Alert`.
-   **UX, dostępność i względy bezpieczeństwa:** Jasne komunikaty o błędach. Pola formularza mają odpowiednie etykiety. Hasło jest maskowane.

### 2. Widok Panelu Administratora
-   **Ścieżka:** `/admin/dashboard`
-   **Główny cel:** Wyświetlenie listy wszystkich quizów i umożliwienie zarządzania nimi.
-   **Kluczowe informacje do wyświetlenia:** Siatka kart z quizami. Każda karta zawiera tytuł, poziom zaawansowania, liczbę pytań i status (`roboczy`/`opublikowany`).
-   **Kluczowe komponenty:** `Card`, `Button` (do tworzenia nowego quizu), `Tooltip` (dla przycisków akcji), `Badge` (dla statusu), `AlertDialog` (do potwierdzenia usunięcia).
-   **UX, dostępność i względy bezpieczeństwa:** Widok chroniony, dostępny tylko dla administratora. Akcje destrukcyjne (usunięcie) wymagają potwierdzenia. Czytelne rozróżnienie statusu quizów.

### 3. Widok Tworzenia Quizu
-   **Ścieżka:** `/admin/create-quiz`
-   **Główny cel:** Generowanie nowego quizu przez AI na podstawie podanych parametrów.
-   **Kluczowe informacje do wyświetlenia:** Formularz z polami: temat, liczba pytań, poziom zaawansowania. Wskaźnik ładowania podczas generowania.
-   **Kluczowe komponenty:** `Form`, `Input`, `Select`, `Button`.
-   **UX, dostępność i względy bezpieczeństwa:** Walidacja pól formularza po stronie klienta. Blokada interfejsu i wyraźny wskaźnik postępu podczas komunikacji z AI.

### 4. Widok Edycji Quizu
-   **Ścieżka:** `/admin/edit-quiz/{quizId}`
-   **Główny cel:** Weryfikacja i modyfikacja treści wygenerowanego quizu przed publikacją.
-   **Kluczowe informacje do wyświetlenia:** Edytowalne pola dla tytułu quizu, treści pytań oraz odpowiedzi. Możliwość zmiany poprawnej odpowiedzi.
-   **Kluczowe komponenty:** `Form`, `Input`, `Textarea`, `RadioGroup`, `Button` "Zapisz zmiany".
-   **UX, dostępność i względy bezpieczeństwa:** Widok chroniony. Jasne wskazanie, która odpowiedź jest obecnie oznaczona jako poprawna.

### 5. Widok Panelu Ucznia
-   **Ścieżka:** `/student/dashboard`
-   **Główny cel:** Wyświetlenie listy dostępnych (opublikowanych) quizów do rozwiązania.
-   **Kluczowe informacje do wyświetlenia:** Siatka kart z quizami. Każda karta zawiera tytuł, poziom zaawansowania, liczbę pytań oraz ostatni wynik (jeśli istnieje).
-   **Kluczowe komponenty:** `Card`, `Button` "Rozpocznij".
-   **UX, dostępność i względy bezpieczeństwa:** Widok chroniony, dostępny tylko dla ucznia. Wyświetlane są tylko opublikowane quizy. Ostatni wynik motywuje do poprawy.

### 6. Widok Rozwiązywania Quizu
-   **Ścieżka:** `/student/quiz/{quizId}`
-   **Główny cel:** Umożliwienie uczniowi interaktywnego odpowiadania na pytania w quizie.
-   **Kluczowe informacje do wyświetlenia:** Aktualne pytanie, cztery opcje odpowiedzi, wskaźnik postępu (np. "Pytanie 3 z 10"), informacja zwrotna po odpowiedzi (poprawna/błędna) oraz wyjaśnienie od AI.
-   **Kluczowe komponenty:** `Card`, `Progress`, `Button` (dla odpowiedzi i nawigacji).
-   **UX, dostępność i względy bezpieczeństwa:** Interfejs jest blokowany po udzieleniu odpowiedzi do czasu otrzymania feedbacku z serwera, co zapobiega podwójnemu kliknięciu. Jasna sygnalizacja wizualna (kolory) poprawności odpowiedzi.

### 7. Widok Podsumowania Quizu
-   **Ścieżka:** `/student/quiz/{quizId}/summary`
-   **Główny cel:** Przedstawienie uczniowi jego ostatecznego wyniku po zakończeniu quizu.
-   **Kluczowe informacje do wyświetlenia:** Końcowy wynik w formacie `X/Y` (np. "8/10").
-   **Kluczowe komponenty:** `Card`, `Button` "Powrót do listy quizów".
-   **UX, dostępność i względy bezpieczeństwa:** Prosty i czytelny komunikat o wyniku. Łatwa nawigacja z powrotem do panelu głównego.

## 3. Mapa podróży użytkownika

### Podróż Administratora
1.  **Logowanie:** Użytkownik ląduje na `/login`, wprowadza dane i zostaje przekierowany na `/admin/dashboard`.
2.  **Tworzenie quizu:** Z panelu klika "Stwórz nowy quiz", przechodzi do `/admin/create-quiz`, wypełnia formularz i inicjuje generowanie przez AI.
3.  **Weryfikacja:** Po wygenerowaniu jest automatycznie przekierowywany do `/admin/edit-quiz/{id}` w celu weryfikacji i edycji quizu.
4.  **Publikacja:** Po zapisaniu zmian wraca do panelu, gdzie może opublikować quiz jednym kliknięciem.
5.  **Zarządzanie:** Z poziomu panelu może w każdej chwili edytować, publikować lub usuwać (z potwierdzeniem) dowolny quiz.

### Podróż Ucznia
1.  **Logowanie:** Użytkownik ląduje na `/login`, wprowadza dane i zostaje przekierowany na `/student/dashboard`.
2.  **Wybór quizu:** Przegląda listę opublikowanych quizów i wybiera jeden, klikając "Rozpocznij".
3.  **Rozwiązywanie:** Przechodzi do `/student/quiz/{id}`. Odpowiada na pytania jedno po drugim, otrzymując natychmiastową informację zwrotną po każdej odpowiedzi.
4.  **Zakończenie:** Po ostatnim pytaniu przechodzi do podsumowania na `/student/quiz/{id}/summary`, gdzie widzi swój wynik.
5.  **Powrót:** Klika przycisk powrotu, aby wrócić do listy quizów, gdzie widzi swój zaktualizowany "ostatni wynik".

## 4. Układ i struktura nawigacji

Aplikacja będzie posiadać główny, dwukolumnowy layout widoczny po zalogowaniu:
-   **Lewy panel nawigacyjny:** Wąska, statyczna kolumna zawierająca logo aplikacji oraz linki nawigacyjne zależne od roli użytkownika (np. "Quizy" dla obu ról, niefunkcjonalny link "Użytkownicy" dla admina w wersji MVP).
-   **Główny obszar treści:** Prawa, szersza kolumna, w której renderowane są poszczególne widoki (`/login`, `/admin/dashboard`, `/student/quiz/{id}` itd.).
-   **Nagłówek:** Zintegrowany z głównym obszarem treści, wyświetlający nazwę zalogowanego użytkownika oraz ikonę wylogowania.

Nawigacja jest oparta na `react-router-dom`. Dostęp do ścieżek `/admin/*` i `/student/*` jest chroniony przez komponent `ProtectedRoute`, który weryfikuje token JWT i rolę użytkownika, przekierowując na `/login` w przypadku braku autoryzacji.

## 5. Kluczowe komponenty

Poniższe komponenty `shadcn/ui` będą kluczowe i reużywalne w całej aplikacji:
-   **`Card`**: Podstawowy kontener do grupowania informacji, używany do wyświetlania quizów na listach, w formularzach i na ekranach podsumowań.
-   **`Button`**: Używany do wszystkich akcji wykonywanych przez użytkownika: logowanie, nawigacja, przesyłanie formularzy, wybieranie odpowiedzi.
-   **`Form` (z `React Hook Form` i `Zod`)**: Standard do budowy wszystkich formularzy, zapewniający walidację i zarządzanie stanem.
-   **`Input`, `Select`, `Textarea`, `RadioGroup`**: Podstawowe elementy składowe formularzy.
-   **`AlertDialog`**: Używany do uzyskania potwierdzenia od użytkownika przed wykonaniem akcji destrukcyjnej, takiej jak usunięcie quizu.
-   **`Toast` (np. `sonner`)**: Do wyświetlania nieblokujących powiadomień systemowych (np. "Quiz został opublikowany", "Błąd serwera").
-   **`Badge`**: Do wizualnego oznaczania statusu quizu ("Roboczy", "Opublikowany") w panelu administratora.
-   **`Tooltip`**: Do dostarczania dodatkowych informacji dla przycisków-ikon, poprawiając dostępność i UX. 