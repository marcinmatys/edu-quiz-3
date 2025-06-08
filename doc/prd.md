# Dokument wymagań produktu (PRD) - EDU-QUIZ

## 1. Przegląd produktu
EDU-QUIZ to aplikacja edukacyjna przeznaczona do tworzenia i przeprowadzania interaktywnych quizów na poziomie szkolnym. System wykorzystuje sztuczną inteligencję (AI) do generowania treści, co ma na celu ułatwienie pracy nauczycielom i zwiększenie zaangażowania uczniów. Aplikacja rozróżnia dwie role użytkowników: administratora, który zarządza quizami i kontami, oraz ucznia, który przegląda, uruchamia i rozwiązuje quizy, otrzymując natychmiastową informację zwrotną.

## 2. Problem użytkownika
Aplikacja adresuje dwa główne problemy:
*   Dla administratora (nauczyciela): Ręczne tworzenie angażujących i zróżnicowanych quizów jest procesem czasochłonnym i wymagającym dużej kreatywności. Brakuje narzędzi, które automatyzują ten proces, zachowując jednocześnie wysoką jakość merytoryczną.
*   Dla ucznia: Tradycyjne metody nauki i weryfikacji wiedzy często są postrzegane jako mało atrakcyjne. Uczniowie potrzebują interaktywnej i angażującej formy nauki, która dostarcza natychmiastowej informacji zwrotnej i motywuje do dalszego rozwoju poprzez element grywalizacji.

## 3. Wymagania funkcjonalne
*   FW-01: Generowanie quizów przez AI na podstawie tematu, liczby pytań i poziomu zaawansowania (klasy I-VIII szkoły podstawowej).
*   FW-02: Pytania w quizach są jednokrotnego wyboru z czterema opcjami odpowiedzi.
*   FW-03: Panel administratora umożliwiający zarządzanie cyklem życia quizu: generowanie, przeglądanie, edycja, zapisywanie, publikowanie i usuwanie.
*   FW-04: Dostęp do dedykowanego konta administratora.
*   FW-05: Interfejs ucznia umożliwiający przeglądanie opublikowanych quizów.
*   FW-06: Możliwość uruchamiania i rozwiązywania quizów przez ucznia.
*   FW-07: Dostęp do dedykowanego konta ucznia.
*   FW-08: Quizy na liście są posortowane według poziomu zaawansowania.
*   FW-09: Uczeń otrzymuje natychmiastową informację zwrotną (poprawna/niepoprawna odpowiedź) wraz z dodatkowym komentarzem od AI.
*   FW-10: Po zakończeniu quizu uczeń widzi podsumowanie wyników (np. 7/10).
*   FW-11: Statystyki (ostatni wynik) wykonania quizu są zapisywane i widoczne na liście dostępnych quizów.

## 4. Granice produktu
W zakresie MVP nie znajdują się następujące funkcjonalności:
*   Zarządzanie kontami użytkowników (w systemie istnieją na stałe jedno konto administratora i jedno konto ucznia).
*   Możliwość przeglądania statystyk ucznia przez administratora.
*   Limit czasowy na rozwiązanie quizu.
*   Możliwość wznowienia przerwanego quizu (należy go rozpocząć od nowa).
*   Różne typy pytań (tylko jednokrotnego wyboru).

## 5. Historyjki użytkowników

### Autentykacja

*   ID: US-001
*   Tytuł: Logowanie do systemu
*   Opis: Jako użytkownik (administrator lub uczeń) chcę móc zalogować się do aplikacji przy użyciu mojej nazwy użytkownika i hasła, aby uzyskać dostęp do przypisanych mi funkcjonalności.
*   Kryteria akceptacji:
    *   System wyświetla formularz logowania z polami na nazwę użytkownika i hasło.
    *   Po wprowadzeniu poprawnych danych administratora i kliknięciu "Zaloguj", użytkownik jest przekierowany do panelu administratora.
    *   Po wprowadzeniu poprawnych danych ucznia i kliknięciu "Zaloguj", użytkownik jest przekierowany do listy quizów.
    *   W przypadku wprowadzenia nieprawidłowych danych, system wyświetla komunikat o błędzie.
    *   Dane logowania są bezpiecznie przechowywane w bazie danych.

### Ścieżka Administratora

*   ID: US-002
*   Tytuł: Generowanie nowego quizu przez AI
*   Opis: Jako administrator chcę wygenerować nowy quiz przy użyciu AI, podając jego temat, liczbę pytań i poziom zaawansowania, aby szybko stworzyć materiał edukacyjny.
*   Kryteria akceptacji:
    *   W panelu administratora znajduje się opcja "Stwórz nowy quiz".
    *   Po jej wybraniu wyświetla się formularz z polami: "Temat", "Liczba pytań", "Poziom zaawansowania" (lista rozwijana, klasy I-VIII).
    *   Pola formularza są walidowane (np. liczba pytań musi być dodatnią liczbą całkowitą).
    *   Po zatwierdzeniu formularza system wysyła zapytanie do AI i wyświetla informację o trwającym procesie generowania.
    *   Wygenerowany quiz (pytania i 4 opcje odpowiedzi dla każdego) jest prezentowany do weryfikacji.

*   ID: US-003
*   Tytuł: Weryfikacja i edycja wygenerowanego quizu
*   Opis: Jako administrator chcę przejrzeć wygenerowany przez AI quiz i mieć możliwość edycji każdego pytania oraz odpowiedzi, aby zapewnić jego jakość merytoryczną przed publikacją.
*   Kryteria akceptacji:
    *   Wygenerowany quiz jest wyświetlany w formie czytelnej listy pytań i odpowiedzi.
    *   Przy każdym pytaniu i odpowiedzi istnieje opcja "Edytuj".
    *   Administrator może zmodyfikować treść pytania oraz każdej z czterech odpowiedzi.
    *   Administrator może oznaczyć inną odpowiedź jako poprawną.
    *   Wprowadzone zmiany są zapisywane.

*   ID: US-004
*   Tytuł: Odrzucenie wygenerowanego quizu
*   Opis: Jako administrator chcę mieć możliwość odrzucenia całego wygenerowanego quizu, jeśli jego jakość jest niezadowalająca.
*   Kryteria akceptacji:
    *   Na ekranie weryfikacji quizu znajduje się przycisk "Odrzuć" lub "Usuń".
    *   Po jego kliknięciu i potwierdzeniu, quiz jest trwale usuwany z systemu.
    *   Administrator jest informowany o pomyślnym usunięciu quizu.

*   ID: US-005
*   Tytuł: Publikacja quizu
*   Opis: Jako administrator chcę opublikować zweryfikowany i poprawiony quiz, aby stał się on widoczny i dostępny dla uczniów.
*   Kryteria akceptacji:
    *   Na ekranie weryfikacji quizu znajduje się przycisk "Zatwierdź i publikuj".
    *   Po jego kliknięciu quiz zmienia status na "opublikowany".
    *   Opublikowany quiz pojawia się na liście quizów dostępnej dla ucznia.
    *   Administrator widzi na liście quizów, które z nich mają status "opublikowany", a które "roboczy".

*   ID: US-006
*   Tytuł: Zarządzanie listą quizów
*   Opis: Jako administrator chcę widzieć listę wszystkich stworzonych quizów (zarówno roboczych, jak i opublikowanych), aby móc nimi zarządzać.
*   Kryteria akceptacji:
    *   Panel administratora wyświetla listę wszystkich quizów.
    *   Lista zawiera informacje takie jak: tytuł/temat, poziom zaawansowania, liczba pytań, status (roboczy/opublikowany).
    *   Z poziomu listy administrator może wejść w edycję quizu roboczego.
    *   Z poziomu listy administrator może usunąć dowolny quiz (po potwierdzeniu).

### Ścieżka Ucznia

*   ID: US-007
*   Tytuł: Przeglądanie listy dostępnych quizów
*   Opis: Jako uczeń chcę widzieć listę wszystkich opublikowanych quizów, posortowaną według poziomu trudności, abym mógł wybrać interesujący mnie test.
*   Kryteria akceptacji:
    *   Po zalogowaniu uczeń widzi listę dostępnych quizów.
    *   Quizy są domyślnie posortowane rosnąco według poziomu zaawansowania.
    *   Każdy element listy zawiera: temat quizu, poziom zaawansowania, liczbę pytań oraz mój ostatni wynik (jeśli quiz był już rozwiązywany).
    *   Jeśli quiz nie był jeszcze rozwiązywany, informacja o wyniku nie jest wyświetlana.

*   ID: US-008
*   Tytuł: Rozwiązywanie quizu
*   Opis: Jako uczeń chcę móc uruchomić wybrany quiz i odpowiadać na pytania, aby sprawdzić swoją wiedzę.
*   Kryteria akceptacji:
    *   Po kliknięciu na quiz z listy, rozpoczyna się jego rozwiązywanie.
    *   Na ekranie wyświetlane jest jedno pytanie i cztery możliwe odpowiedzi.
    *   Uczeń może wybrać tylko jedną odpowiedź.
    *   Po wybraniu odpowiedzi przechodzi do następnego pytania.
    *   Quiz nie ma limitu czasowego.
    *   Jeśli przerwę quiz w trakcie, mój postęp nie jest zapisywany i muszę zacząć od nowa.

*   ID: US-009
*   Tytuł: Otrzymywanie natychmiastowej informacji zwrotnej
*   Opis: Jako uczeń, po udzieleniu odpowiedzi na pytanie, chcę od razu dowiedzieć się, czy była ona poprawna, oraz otrzymać krótki komentarz od AI, aby lepiej zrozumieć zagadnienie.
*   Kryteria akceptacji:
    *   Po wybraniu odpowiedzi system natychmiast oznacza ją jako poprawną (np. na zielono) lub niepoprawną (np. na czerwono).
    *   W przypadku błędnej odpowiedzi, system wskazuje poprawną odpowiedź.
    *   Pod odpowiedzią pojawia się krótki, wygenerowany przez AI komentarz dotyczący pytania/odpowiedzi.

*   ID: US-010
*   Tytuł: Zakończenie quizu i przegląd wyników
*   Opis: Jako uczeń, po odpowiedzeniu na wszystkie pytania, chcę zobaczyć swoje podsumowanie wyników, aby ocenić poziom swojej wiedzy.
*   Kryteria akceptacji:
    *   Po udzieleniu odpowiedzi na ostatnie pytanie, wyświetla się ekran podsumowania.
    *   Ekran podsumowania zawiera wynik w formacie `poprawne/wszystkie` (np. 7/10).
    *   Wynik zostaje zapisany na moim koncie jako "ostatni wynik" dla tego quizu.
    *   Z ekranu podsumowania mogę wrócić do listy quizów.

## 6. Kryteria sukcesu
*   Zastosowanie AI pozwala administratorowi w łatwy i szybki sposób tworzyć nowe, angażujące quizy.
*   Administrator ma do dyspozycji prosty i intuicyjny interfejs pozwalający zarządzać quizami na każdym etapie ich cyklu życia.
*   Uczeń może przeglądać, uruchamiać i wykonywać quizy w sposób płynny i bezproblemowy, wykorzystując prosty i intuicyjny interfejs.
*   System jest stabilny i zapewnia poprawne działanie kluczowych funkcjonalności (generowanie, rozwiązywanie, zapisywanie wyników). 