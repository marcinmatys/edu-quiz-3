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