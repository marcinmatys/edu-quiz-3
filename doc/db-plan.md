<conversation_summary>
<decisions>
1.  Rola użytkownika (`role`) będzie przechowywana jako tekst ('admin', 'student').
2.  Zostanie utworzona osobna tabela `levels` do przechowywania poziomów zaawansowania, zawierająca pola `code` (I-VIII), `description` i `level` (1-8). Tabela ta zostanie wstępnie wypełniona danymi podczas inicjalizacji bazy.
3.  Komentarz AI do pytania nie będzie zapisywany w bazie danych.
4.  Wynik quizu będzie przechowywany w dwóch osobnych kolumnach liczbowych (`score`, `max_score`).
5.  Usunięcie quizu spowoduje kaskadowe usunięcie wszystkich powiązanych z nim pytań i odpowiedzi (`ON DELETE CASCADE`).
6.  Edycja opublikowanego quizu, na który odpowiedział już uczeń, zostanie zablokowana na poziomie logiki aplikacji.
7.  W tabeli z quizami dodana zostanie kolumna `creator_id` z typem danych INTEGER i ograniczeniem `NOT NULL`.
8.  Przechowywany będzie tylko ostatni wynik quizu dla danego ucznia. Zostanie to zapewnione przez nałożenie ograniczenia `UNIQUE` na parę kluczy (`user_id`, `quiz_id`) w tabeli `results`.
9.  Kolejność pytań w quizie oraz odpowiedzi w pytaniu nie musi być stała i może być losowa. Nie ma potrzeby dodawania kolumn `position`.
10. Zostaną zdefiniowane maksymalne długości dla pól tekstowych: `username` (64), `quizzes.title` (256), `questions.text` (512), `answers.text` (128).
11. Usunięcie użytkownika lub quizu spowoduje kaskadowe usunięcie powiązanych z nimi wyników w tabeli `results` (`ON DELETE CASCADE`).
</decisions>

<matched_recommendations>
1.  **Logika w warstwie aplikacji**: Kontrola dostępu (odpowiednik RLS) oraz reguły biznesowe (np. blokowanie edycji opublikowanego quizu) zostaną zaimplementowane w warstwie aplikacji (FastAPI), a nie na poziomie bazy danych.
2.  **Integralność referencyjna**: Zostaną użyte klucze obce (`FOREIGN KEY`) z odpowiednimi ograniczeniami `ON DELETE CASCADE`, aby zapewnić spójność danych między tabelami.
3.  **Strategia indeksowania**: Zostaną utworzone indeksy na kolumnach często używanych do filtrowania i sortowania (`quizzes.status`, `quizzes.level`) oraz na wszystkich kluczach obcych w celu optymalizacji wydajności.
4.  **Bezpieczeństwo haseł**: Hasła użytkowników będą przechowywane w bazie danych jako bezpieczne skróty (hashe).
5.  **Spójność typów danych**: Zostanie użyta spójna konwencja typów danych, np. `INTEGER` z ograniczeniem `CHECK IN (0, 1)` dla wartości `BOOLEAN` (np. `answers.is_correct`).
6.  **Wypełnianie bazy danych (Seeding)**: Zostanie przygotowany skrypt do inicjalnego wypełnienia bazy danych wymaganymi danymi (konta użytkowników, poziomy zaawansowania).
7.  **Znaczniki czasu**: Kluczowe tabele (`users`, `quizzes`, `results`) będą zawierały kolumny `created_at` i `updated_at` do śledzenia zmian.
8.  **Konwencja nazewnictwa**: Zostanie zastosowana spójna konwencja nazewnictwa w stylu `snake_case` dla tabel i kolumn, z nazwami tabel w liczbie mnogiej.
</matched_recommendations>

<database_planning_summary> 
Na podstawie przeprowadzonych ustaleń, schemat bazy danych SQLite dla MVP aplikacji EDU-QUIZ zostanie zaprojektowany w celu obsługi podstawowych wymagań funkcjonalnych, z naciskiem na integralność danych i logikę zaimplementowaną w warstwie aplikacyjnej.

**Główne wymagania dotyczące schematu:**
*   Obsługa dwóch ról użytkowników: administratora i ucznia.
*   Przechowywanie quizów wraz z ich statusem (roboczy/opublikowany) i poziomem zaawansowania.
*   Struktura pytań jednokrotnego wyboru z czterema odpowiedziami.
*   Zapisywanie tylko ostatniego wyniku dla każdego quizu rozwiązanego przez ucznia.
*   Zapewnienie integralności danych poprzez użycie kluczy obcych i polityk usuwania kaskadowego.

**Kluczowe encje i ich relacje:**

*   `users` (Użytkownicy)
    *   `id` (INTEGER, PK), `username` (VARCHAR(64), UNIQUE), `hashed_password` (VARCHAR), `role` (TEXT), `created_at`, `updated_at`.
*   `levels` (Poziomy zaawansowania)
    *   `id` (INTEGER, PK), `code` (VARCHAR), `description` (VARCHAR), `level` (INTEGER).
*   `quizzes` (Quizy)
    *   `id` (INTEGER, PK), `title` (VARCHAR(256)), `status` (TEXT), `level_id` (FK do `levels.id`).
    *   Relacja: Jeden poziom (`level`) może być przypisany do wielu quizów.
*   `questions` (Pytania)
    *   `id` (INTEGER, PK), `text` (VARCHAR(512)), `quiz_id` (FK do `quizzes.id`, ON DELETE CASCADE).
    *   Relacja: Jeden quiz (`quiz`) składa się z wielu pytań.
*   `answers` (Odpowiedzi)
    *   `id` (INTEGER, PK), `text` (VARCHAR(128)), `is_correct` (INTEGER), `question_id` (FK do `questions.id`, ON DELETE CASCADE).
    *   Relacja: Jedno pytanie (`question`) ma wiele odpowiedzi.
*   `results` (Wyniki)
    *   `id` (INTEGER, PK), `score` (INTEGER), `max_score` (INTEGER), `user_id` (FK do `users.id`, ON DELETE CASCADE), `quiz_id` (FK do `quizzes.id`, ON DELETE CASCADE), `created_at`, `updated_at`.
    *   Ograniczenie: `UNIQUE(user_id, quiz_id)`.
    *   Relacja: Jeden użytkownik (`user`) może mieć wiele wyników, a jeden quiz (`quiz`) może mieć wiele wyników.

**Kwestie bezpieczeństwa i skalowalności:**
*   **Bezpieczeństwo**: Cała logika autoryzacji i kontroli dostępu do danych będzie realizowana po stronie serwera FastAPI. Hasła w bazie danych będą hashowane.
*   **Skalowalność**: Dla potrzeb MVP, skalowalność jest zapewniona przez odpowiednie indeksowanie kluczowych kolumn. Projekt nie uwzględnia mechanizmów takich jak partycjonowanie, które są zbędne na tym etapie.

</database_planning_summary>

<unresolved_issues>
Wszystkie kwestie poruszone w trakcie dyskusji zostały rozwiązane, a decyzje projektowe zostały podjęte. Nie ma nierozwiązanych problemów wymagających dalszych wyjaśnień na tym etapie planowania schematu bazy danych.
</unresolved_issues>
</conversation_summary>