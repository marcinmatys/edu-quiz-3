Jesteś doświadczonym menedżerem produktu, którego zadaniem jest stworzenie kompleksowego dokumentu wymagań produktu (PRD) w oparciu o poniższe opisy:

<project_description>
### Cel projektu
Stworzenie aplikacji umożliwiającej tworzenie i przeprowadzanie quizów edukacyjnych na poziomie szkolnym.
Quizy mają służyć zarówno jako forma zabawy, jak i narzędzie edukacyjne.
Quizy obejmują różnorodne tematy oraz poziomy zaawansowania.
Quizy mają być generowaneprzy wsparciu AI

### Zestaw funkcjonalności
- Generowanie quizów przez AI z wybranej tematyki na wybranym poziomie zaawansowania
- Zarządzanie quizami: przeglądanie, generowanie, modyfikacja, zapisywanie, usuwanie
- Wykonywanie quizów: przeglądanie, uruchamianie, wykonywanie 
- Konto administratora pozwalające na zarządzanie quizami
- Konto ucznia pozwalające na wykonywanie quizów
- Użytkownicy widzą quizy posortowane według poziomu zaawansowania
- Po wykonaniu quizu uczeń widzi statystyki swoich odpowiedzi
- Statystyki wykonania quizu zapisywane są na koncie ucznia
- Statystyki wykonanych quizów widoczne są na liście dostępnych quizów


### Co NIE wchodzi w zakres MVP
- Zarządzanie użytkownikami. Na stałe dostępne jest jedno konto administratora i jedno konto ucznia
- Przeglądanie statystyk ucznia przez administratora

### Kryteria sukcesu
- Zastosowanie AI pozwala administratorowi w łatwy i szybki sposób tworzyć nowe quizy.
- Admistrator ma do dyspozycji prosty i intuicyjny interfejs pozwalający zarządzać quizami.
- Uczeń może przeglądać, uruchamiać i wykonywać quizy wykorzystując prosty i intuicyjny interfejs 
</project_description>

<project_details>
<conversation_summary>
<decisions>
1.  **Dane wejściowe do generowania quizu:** Do wygenerowania quizu wymagane są: temat, liczba pytań oraz poziom zaawansowania (od I do VIII klasy szkoły podstawowej). Pytania będą jednokrotnego wyboru z czterema opcjami odpowiedzi.
2.  **Weryfikacja przez administratora:** Administrator weryfikuje wygenerowane pytania, ma możliwość edycji poszczególnych pytań i odpowiedzi lub odrzucenia całego quizu, a na końcu zatwierdza quiz do publikacji.
3.  **Struktura i wykonanie quizu:** Quizy nie mają limitu czasowego. Po przerwaniu quizu należy go rozpocząć od nowa.
4.  **Informacje zwrotne i statystyki dla ucznia:** W trakcie rozwiązywania quizu uczeń natychmiast widzi, czy odpowiedź jest poprawna, i otrzymuje dodatkowy feedback od AI. Po zakończeniu quizu widzi wynik w formacie `poprawne/wszystkie` (np. 7/10). Na liście quizów widoczny jest ostatni uzyskany wynik.
5.  **Konta użytkowników:** W wersji MVP konta administratora i ucznia będą na stałe zapisane w bazie danych.
6.  **Walidacja:** Zostanie wprowadzona podstawowa walidacja danych wprowadzanych przez administratora.
</decisions>

<matched_recommendations>
1.  **Uproszczenie MVP:** Ograniczono się do jednego typu pytań (jednokrotnego wyboru), aby uprościć implementację.
2.  **Proces publikacji:** Wdrożono jasny proces: generowanie (AI), weryfikacja i edycja (administrator), a następnie publikacja.
3.  **Zdefiniowane poziomy trudności:** Utworzono zamkniętą listę poziomów zaawansowania (klasy I-VIII), co ułatwi sortowanie i generowanie treści.
4.  **Brak wznawiania quizu:** W celu uproszczenia MVP przerwany quiz nie jest zapisywany i trzeba go zacząć od nowa.
5.  **Przechowywanie danych logowania:** Dane logowania będą przechowywane w bazie danych, a nie w kodzie źródłowym.
</matched_recommendations>

<prd_planning_summary>
Na podstawie zebranych informacji, PRD dla MVP powinno opisywać system z dwiema kluczowymi rolami: Administratora i Ucznia.

**Główne wymagania funkcjonalne produktu:**
*   **Generator Quizów (AI):** System musi umożliwiać generowanie quizów na podstawie tematu, liczby pytań i poziomu trudności (klasy I-VIII) podanych przez administratora. Quizy składają się z pytań jednokrotnego wyboru (4 opcje).
*   **Panel Administratora:** Administrator zarządza cyklem życia quizu: generuje, przegląda, edytuje (na poziomie pojedynczych pytań), zatwierdza, publikuje i usuwa quizy.
*   **Interfejs Ucznia:** Uczeń ma dostęp do listy opublikowanych quizów, posortowanych według poziomu trudności. Może uruchomić dowolny quiz. W trakcie rozwiązywania otrzymuje natychmiastową informację o poprawności odpowiedzi oraz dodatkowy komentarz od AI. Po zakończeniu widzi swój wynik, który jest zapisywany jako ostatni na liście główniej.

**Kluczowe historie użytkownika i ścieżki korzystania:**
*   **Ścieżka Administratora:** Administrator loguje się, tworzy nowy quiz podając jego parametry, weryfikuje i poprawia treść wygenerowaną przez AI, a następnie publikuje go, udostępniając go uczniom.
*   **Ścieżka Ucznia:** Uczeń loguje się, przegląda listę dostępnych quizów wraz ze swoimi ostatnimi wynikami, wybiera i rozwiązuje quiz, otrzymując informację o poprawności odpowiedzi i krótki komentarz AI, a na końcu poznaje swój wynik końcowy.

</prd_planning_summary>

<unresolved_issues>
1.  **Model Danych:** Projekt szczegółowego modelu bazy danych (schemat tabel dla quizów, pytań, odpowiedzi itd.) został odłożony na później.
2.  **Prompt Engineering:** Szczegółowa konstrukcja promptów dla AI, zarówno do generowania quizów, jak i do dostarczania feedbacku w czasie rzeczywistym, wymaga dalszych prac.
3.  **Feedback AI w czasie rzeczywistym:** Należy dokładnie zdefiniować, jakiego rodzaju "dodatkowy feedback" ma dostarczać AI podczas odpowiedzi ucznia. Konieczne jest określenie jego zakresu, formy i sposobu generowania, ponieważ ma to kluczowy wpływ na złożoność implementacji.
</unresolved_issues>
</conversation_summary>
</project_details>

Wykonaj następujące kroki, aby stworzyć kompleksowy i dobrze zorganizowany dokument:

1. Podziel PRD na następujące sekcje:
   a. Przegląd projektu
   b. Problem użytkownika
   c. Wymagania funkcjonalne
   d. Granice projektu
   e. Historie użytkownika
   f. Kryteria sukcesu

2. W każdej sekcji należy podać szczegółowe i istotne informacje w oparciu o opis projektu i odpowiedzi na pytania wyjaśniające. Upewnij się, że:
   - Używasz jasnego i zwięzłego języka
   - W razie potrzeby podajesz konkretne szczegóły i dane
   - Zachowujesz spójność w całym dokumencie
   - Odnosisz się do wszystkich punktów wymienionych w każdej sekcji

3. Podczas tworzenia historyjek użytkownika i kryteriów akceptacji
   - Wymień WSZYSTKIE niezbędne historyjki użytkownika, w tym scenariusze podstawowe, alternatywne i skrajne.
   - Przypisz unikalny identyfikator wymagań (np. US-001) do każdej historyjki użytkownika w celu bezpośredniej identyfikowalności.
   - Uwzględnij co najmniej jedną historię użytkownika specjalnie dla bezpiecznego dostępu lub uwierzytelniania, jeśli aplikacja wymaga identyfikacji użytkownika lub ograniczeń dostępu.
   - Upewnij się, że żadna potencjalna interakcja użytkownika nie została pominięta.
   - Upewnij się, że każda historia użytkownika jest testowalna.

Użyj następującej struktury dla każdej historii użytkownika:
- ID
- Tytuł
- Opis
- Kryteria akceptacji

4. Po ukończeniu PRD przejrzyj go pod kątem tej listy kontrolnej:
   - Czy każdą historię użytkownika można przetestować?
   - Czy kryteria akceptacji są jasne i konkretne?
   - Czy mamy wystarczająco dużo historyjek użytkownika, aby zbudować w pełni funkcjonalną aplikację?
   - Czy uwzględniliśmy wymagania dotyczące uwierzytelniania i autoryzacji (jeśli dotyczy)?

5. Formatowanie PRD:
   - Zachowaj spójne formatowanie i numerację.
   - Nie używaj pogrubionego formatowania w markdown ( ** ).
   - Wymień WSZYSTKIE historyjki użytkownika.
   - Sformatuj PRD w poprawnym markdown.

Przygotuj PRD z następującą strukturą:

```markdown
# Dokument wymagań produktu (PRD) - EDU-QUIZ
## 1. Przegląd produktu
## 2. Problem użytkownika
## 3. Wymagania funkcjonalne
## 4. Granice produktu
## 5. Historyjki użytkowników
## 6. Kryteria sukcesu
```

Pamiętaj, aby wypełnić każdą sekcję szczegółowymi, istotnymi informacjami w oparciu o opis projektu i nasze pytania wyjaśniające. Upewnij się, że PRD jest wyczerpujący, jasny i zawiera wszystkie istotne informacje potrzebne do dalszej pracy nad produktem.

Ostateczny wynik powinien składać się wyłącznie z PRD zgodnego ze wskazanym formatem w markdown, który zapiszesz w pliku doc/prd.md