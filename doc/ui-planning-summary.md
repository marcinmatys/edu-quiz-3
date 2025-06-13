<conversation_summary>
<decisions>
1.  **Routing**: Aplikacja będzie aplikacją jednostronicową (SPA) z osobnymi, chronionymi grupami tras dla każdej roli: `/admin/*` i `/student/*`. Przekierowanie na odpowiednią ścieżkę nastąpi po zalogowaniu w zależności od roli użytkownika.
2.  **Wygląd list quizów**: Zarówno dla administratora, jak i ucznia, listy quizów będą prezentowane jako siatka kafelków (komponent `Card` z shadcn/ui), a nie tabela. Każdy kafelek będzie zawierał kluczowe informacje i ikony akcji (`Edytuj`, `Publikuj`, `Usuń` dla admina; `Rozpocznij` dla ucznia).
3.  **Proces rozwiązywania quizu**: Quiz jest ładowany w całości przy uruchomieniu. Postęp jest wskazywany prostym tekstem ("Pytanie X z Y"). Po każdej odpowiedzi interfejs jest blokowany do czasu otrzymania odpowiedzi z API (`POST /.../check-answer`).
4.  **Informacja zwrotna**: Po odpowiedzi, przyciski są kolorowane (zielony/czerwony), a poprawna odpowiedź jest wskazywana w razie błędu. Pod odpowiedziami wyświetlane jest wyjaśnienie od AI. Przycisk "Następne pytanie" staje się aktywny dopiero po otrzymaniu feedbacku.
5.  **Generowanie quizu**: Proces generowania quizu przez AI (<10s) będzie blokował UI. Po pomyślnym utworzeniu, administrator jest automatycznie przekierowywany do widoku edycji nowo utworzonego quizu.
6.  **Nawigacja i Układ**: Nawigacja główna znajdzie się w panelu po lewej stronie. Admin będzie miał link do "Quizy". Uczeń również będzie miał link "Quizy", prowadzący do jego widoku listy. Admin będzie miał też link do "Użytkownicy", ale po uruchomieniu będzie tylko informacja, że funkcja nie jest dostępna w MVP. Ikona wylogowania znajdzie się w nagłówku aplikacji.
7.  **Obsługa błędów**: Błędy globalne (np. problemy z połączeniem) będą sygnalizowane za pomocą powiadomień "toast".
8.  **Responsywność i Dostępność**: Wersja MVP będzie przeznaczona wyłącznie na komputery stacjonarne. Kwestie zaawansowanej dostępności (WCAG) nie są priorytetem na tym etapie.
9.  **Edycja quizu**: Wersja MVP będzie wspierać jedynie modyfikację tekstu istniejących pytań i odpowiedzi, bez dodawania i usuwania elementów.
10. **Podsumowanie quizu**: Ekran podsumowania dla ucznia będzie minimalistyczny – wyświetli tylko wynik (np. "8/10") i przycisk powrotu do listy quizów.
</decisions>
<matched_recommendations>
1.  **Architektura komponentów**: Zostanie zastosowana struktura folderów dzieląca komponenty na widoki (`/views`), funkcje biznesowe (`/features`) oraz reużywalne elementy UI (`/ui`), co jest zgodne z propozycją.
2.  **Routing i Ochrona**: Do nawigacji zostanie użyty `react-router-dom`. Zostanie zaimplementowany komponent `ProtectedRoute` oraz osobne ścieżki (`/admin/*`, `/student/*`) w celu separacji ról i ochrony dostępu.
3.  **Zarządzanie stanem**: Stan globalny (uwierzytelnienie, dane użytkownika) będzie zarządzany przez `React Context API`. Stan serwera (zapytania do API, buforowanie, mutacje) będzie obsługiwany przez bibliotekę `TanStack Query (React Query)`.
4.  **Formularze**: Do budowy formularzy (logowanie, tworzenie quizu) zostanie wykorzystana biblioteka `React Hook Form` w połączeniu z `Zod` do walidacji, co zapewni sprawną integrację z komponentami `Form` z `shadcn/ui`.
5.  **Klient API**: Zostanie stworzony scentralizowany klient API (wrapper), który automatycznie dołączy token uwierzytelniający do zapytań i obsłuży podstawowe błędy.
6.  **Przepływ rozwiązywania quizu**: Komponent do rozwiązywania quizu będzie zarządzał stanem pytań lokalnie. Po każdej odpowiedzi zablokuje UI, wywoła API, a następnie zaktualizuje interfejs o wynik, wyjaśnienie poniżej odpowiedzi i odblokuje nawigację do następnego pytania.
7.  **Stylowanie**: Wszystkie style będą implementowane za pomocą `Tailwind CSS`, z maksymalnym wykorzystaniem komponentów i wariantów z `shadcn/ui` dla zachowania spójności wizualnej.
8.  **Przepływ wylogowania**: Przycisk wylogowania wyczyści stan globalny (token, profil) i programowo przekieruje użytkownika na stronę logowania.
9.  **Potwierdzenia akcji**: Akcje destrukcyjne, takie jak usuwanie quizu, będą wymagały od użytkownika potwierdzenia za pomocą modalu `AlertDialog`.
10. **Komponenty UI**: Listy quizów dla obu ról zostaną zaimplementowane przy użyciu kompozycji komponentów `Card`, `Button` i `Tooltip` z `shadcn/ui` w celu stworzenia nowoczesnego interfejsu w formie siatki.
</matched_recommendations>
<ui_architecture_planning_summary>
Na podstawie przeprowadzonej dyskusji, architektura interfejsu użytkownika dla MVP aplikacji EDU-QUIZ zostanie oparta na nowoczesnym stosie technologicznym, w skład którego wchodzą React 19, `shadcn/ui` i `Tailwind CSS`. Aplikacja będzie działać jako SPA (Single Page Application) przeznaczona na desktopy.

**Kluczowe Widoki i Przepływy Użytkownika:**
-   **Autentykacja**: Użytkownik loguje się przez formularz na stronie `/login`. Po pomyślnym zalogowaniu, na podstawie roli, jest przekierowywany do odpowiedniego panelu.
-   **Panel Administratora (`/admin/*`)**:
    -   Główny widok (`/admin/dashboard`) to siatka kart reprezentujących wszystkie quizy (robocze i opublikowane). Karty umożliwiają edycję, usunięcie (z potwierdzeniem) oraz publikację quizu.
    -   Tworzenie quizu odbywa się przez formularz, który po wysłaniu (`POST /quizzes`) i sukcesie, przekierowuje do widoku edycji.
    -   Edycja quizu pozwala na modyfikację tekstów pytań i odpowiedzi.
-   **Panel Ucznia (`/student/*`)**:
    -   Główny widok (`/student/dashboard`) to siatka kart z opublikowanymi quizami.
    -   Rozwiązywanie quizu (`/student/quiz/{id}`) to widok "krok po kroku", gdzie po każdej odpowiedzi użytkownik otrzymuje natychmiastową informację zwrotną wraz z wyjaśnieniem od AI.
    -   Po zakończeniu quizu wyświetlane jest podsumowanie z wynikiem i opcją powrotu do listy.

**Integracja z API i Zarządzanie Stanem:**
Architektura będzie silnie zorientowana na efektywną komunikację z API. `TanStack Query (React Query)` posłuży jako warstwa do zarządzania stanem serwera, obsługując pobieranie danych, buforowanie, stany ładowania i błędy. Stan globalny aplikacji, taki jak dane zalogowanego użytkownika i token JWT, będzie przechowywany w `React Context`. Scentralizowany klient API uprości wysyłanie zautoryzowanych żądań. Formularze będą zarządzane przez `React Hook Form` i `Zod`, co zapewni solidną walidację po stronie klienta.

**Bezpieczeństwo i Kwestie Techniczne:**
Bezpieczeństwo frontendu opierać się będzie na chronionych trasach (`ProtectedRoute`), które uniemożliwią dostęp do paneli `/admin` i `/student` bez ważnego tokena JWT. Separacja ścieżek dodatkowo odizoluje od siebie widoki i logikę poszczególnych ról. Cała logika biznesowa i autoryzacja jest zabezpieczona po stronie backendu, a frontend jedynie konsumuje odpowiednie endpointy. MVP nie obejmuje zaawansowanych funkcji dostępności ani designu mobilnego.
</ui_architecture_planning_summary>
<unresolved_issues>
-   **Mechanizm publikacji quizu**: Należy jednoznacznie zdefiniować, w jaki sposób akcja "Publikuj" na karcie quizu w panelu administratora przekłada się na wywołanie API. Najprawdopodobniej będzie to aktualizacja statusu quizu za pomocą żądania `PUT /quizzes/{quiz_id}` z odpowiednim ciałem.
-   **Wygląd nawigacji**: Potwierdzono, że nawigacja będzie z lewej strony, a link "Użytkownicy" dla admina nie będzie funkcjonalny w MVP. Należy zaprojektować dokładny wygląd i zachowanie tego panelu nawigacyjnego (np. czy jest zwijany).
</unresolved_issues>
</conversation_summary> 