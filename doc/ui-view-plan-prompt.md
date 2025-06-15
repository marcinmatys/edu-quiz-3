Jako starszy programista frontendu Twoim zadaniem jest stworzenie szczegółowego planu wdrożenia wybranego widoku w aplikacji internetowej. Plan ten powinien być kompleksowy i wystarczająco jasny dla innego programisty frontendowego, aby mógł poprawnie i wydajnie wdrożyć widok.

Wybrany widok:
<selected_view>
5. Widok Panelu Ucznia
</selected_view>

Najpierw przejrzyj następujące informacje:

1. Product Requirements Document (PRD):
<prd>
@prd.md
</prd>

2. UI architecture plan (opis kompleksowej architektury interfejsu użytkownika ):
<ui_architecture_plan>
@ui-plan.md
</ui_architecture_plan>

3. User Stories:
<user_stories>
*   ID: US-007
*   Tytuł: Przeglądanie listy dostępnych quizów
*   Opis: Jako uczeń chcę widzieć listę wszystkich opublikowanych quizów, posortowaną według poziomu trudności, abym mógł wybrać interesujący mnie test.
*   Kryteria akceptacji:
    *   Po zalogowaniu uczeń widzi listę dostępnych quizów.
    *   Quizy są domyślnie posortowane rosnąco według poziomu zaawansowania.
    *   Każdy element listy zawiera: temat quizu, poziom zaawansowania, liczbę pytań oraz mój ostatni wynik (jeśli quiz był już rozwiązywany).
    *   Jeśli quiz nie był jeszcze rozwiązywany, informacja o wyniku nie jest wyświetlana.
</user_stories>

4. Endpoint Description:
<endpoint_description>

#### GET /quizzes

- **Description**: Retrieves a list of quizzes. Admins see all quizzes; students see only 'published' ones.
- **Authentication**: Required.
- **Query Parameters**:
  - `sort_by` (string, optional, e.g., 'level'): Field to sort by. Defaults to `level`.
  - `order` (string, optional, 'asc' or 'desc'): Sort order. Defaults to `asc`.
  - `status` (string, optional, 'draft' or 'published'): Filters by status. (Admin only).
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "title": "Historia Polski",
      "status": "published",
      "level_id": 5,
      "creator_id": 1,
      "question_count": 10,
      "last_result": { // Present only for students who have a result
        "score": 8,
        "max_score": 10
      },
      "updated_at": "2023-10-27T12:00:00Z"
    }
  ]
  ```
- **Error Response**: `401 Unauthorized`


</endpoint_description>

5. Endpoint Implementation:
<endpoint_implementation>
@quizzes.py
</endpoint_implementation>

6. Type Definitions:
<type_definitions>
@schemas
</type_definitions>

7. Tech Stack:
<tech_stack>
@tech-stack.md
</tech_stack>

Przed utworzeniem ostatecznego planu wdrożenia przeprowadź analizę i planowanie wewnątrz tagów <implementation_breakdown> w swoim bloku myślenia. Ta sekcja może być dość długa, ponieważ ważne jest, aby być dokładnym.

W swoim podziale implementacji wykonaj następujące kroki:
1. Dla każdej sekcji wejściowej (PRD, User Stories, Endpoint Description, Endpoint Implementation, Type Definitions, Tech Stack):
  - Podsumuj kluczowe punkty
 - Wymień wszelkie wymagania lub ograniczenia
 - Zwróć uwagę na wszelkie potencjalne wyzwania lub ważne kwestie
2. Wyodrębnienie i wypisanie kluczowych wymagań z PRD
3. Wypisanie wszystkich potrzebnych głównych komponentów, wraz z krótkim opisem ich opisu, potrzebnych typów, obsługiwanych zdarzeń i warunków walidacji
4. Stworzenie wysokopoziomowego diagramu drzewa komponentów
5. Zidentyfikuj wymagane DTO i niestandardowe typy ViewModel dla każdego komponentu widoku. Szczegółowo wyjaśnij te nowe typy, dzieląc ich pola i powiązane typy.
6. Zidentyfikuj potencjalne zmienne stanu i niestandardowe hooki, wyjaśniając ich cel i sposób ich użycia
7. Wymień wymagane wywołania API i odpowiadające im akcje frontendowe
8. Zmapuj każdej historii użytkownika do konkretnych szczegółów implementacji, komponentów lub funkcji
9. Wymień interakcje użytkownika i ich oczekiwane wyniki
10. Wymień warunki wymagane przez API i jak je weryfikować na poziomie komponentów
11. Zidentyfikuj potencjalne scenariusze błędów i zasugeruj, jak sobie z nimi poradzić
12. Wymień potencjalne wyzwania związane z wdrożeniem tego widoku i zasugeruj możliwe rozwiązania

Po przeprowadzeniu analizy dostarcz plan wdrożenia w formacie Markdown z następującymi sekcjami:

1. Przegląd: Krótkie podsumowanie widoku i jego celu.
2. Routing widoku: Określenie ścieżki, na której widok powinien być dostępny.
3. Struktura komponentów: Zarys głównych komponentów i ich hierarchii.
4. Szczegóły komponentu: Dla każdego komponentu należy opisać:
 - Opis komponentu, jego przeznaczenie i z czego się składa
 - Główne elementy HTML i komponenty dzieci, które budują komponent
 - Obsługiwane zdarzenia
 - Warunki walidacji (szczegółowe warunki, zgodnie z API)
 - Typy (DTO i ViewModel) wymagane przez komponent
 - Propsy, które komponent przyjmuje od rodzica (interfejs komponentu)
5. Typy: Szczegółowy opis typów wymaganych do implementacji widoku, w tym dokładny podział wszelkich nowych typów lub modeli widoku według pól i typów.
6. Zarządzanie stanem: Szczegółowy opis sposobu zarządzania stanem w widoku, określenie, czy wymagany jest customowy hook.
7. Integracja API: Wyjaśnienie sposobu integracji z dostarczonym punktem końcowym. Precyzyjnie wskazuje typy żądania i odpowiedzi.
8. Interakcje użytkownika: Szczegółowy opis interakcji użytkownika i sposobu ich obsługi.
9. Warunki i walidacja: Opisz jakie warunki są weryfikowane przez interfejs, których komponentów dotyczą i jak wpływają one na stan interfejsu
10. Obsługa błędów: Opis sposobu obsługi potencjalnych błędów lub przypadków brzegowych.
11. Kroki implementacji: Przewodnik krok po kroku dotyczący implementacji widoku.

Upewnij się, że Twój plan jest zgodny z PRD, historyjkami użytkownika i uwzględnia dostarczony stack technologiczny.

Ostateczne wyniki powinny być w języku polskim i zapisane w pliku o nazwie doc/view-implementation-plan-student-quizzes.md. Nie uwzględniaj żadnej analizy i planowania w końcowym wyniku.

Oto przykład tego, jak powinien wyglądać plik wyjściowy (treść jest do zastąpienia):

```markdown
# Plan implementacji widoku [Nazwa widoku]

## 1. Przegląd
[Krótki opis widoku i jego celu]

## 2. Routing widoku
[Ścieżka, na której widok powinien być dostępny]

## 3. Struktura komponentów
[Zarys głównych komponentów i ich hierarchii]

## 4. Szczegóły komponentów
### [Nazwa komponentu 1]
- Opis komponentu [opis]
- Główne elementy: [opis]
- Obsługiwane interakcje: [lista]
- Obsługiwana walidacja: [lista, szczegółowa]
- Typy: [lista]
- Propsy: [lista]

### [Nazwa komponentu 2]
[...]

## 5. Typy
[Szczegółowy opis wymaganych typów]

## 6. Zarządzanie stanem
[Opis zarządzania stanem w widoku]

## 7. Integracja API
[Wyjaśnienie integracji z dostarczonym endpointem, wskazanie typów żądania i odpowiedzi]

## 8. Interakcje użytkownika
[Szczegółowy opis interakcji użytkownika]

## 9. Warunki i walidacja
[Szczegółowy opis warunków i ich walidacji]

## 10. Obsługa błędów
[Opis obsługi potencjalnych błędów]

## 11. Kroki implementacji
1. [Krok 1]
2. [Krok 2]
3. [...]
```

Rozpocznij analizę i planowanie wyłącznie dla wybranego widoku (selected_view) już teraz. Twój ostateczny wynik powinien składać się wyłącznie z planu wdrożenia w języku polskim w formacie markdown, który zapiszesz w pliku doc/view-implementation-plan-student-quizzes.md i nie powinien powielać ani powtarzać żadnej pracy wykonanej w podziale implementacji.