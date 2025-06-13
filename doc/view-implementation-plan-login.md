# Plan implementacji widoku logowania

## 1. Przegląd
Widok logowania jest pierwszym ekranem, z którym użytkownik ma interakcję. Jego głównym celem jest uwierzytelnienie użytkownika na podstawie nazwy użytkownika i hasła. Po pomyślnej weryfikacji, system przyznaje użytkownikowi dostęp do odpowiedniej sekcji aplikacji (panelu administratora lub panelu ucznia) w oparciu o jego rolę. Widok musi również obsługiwać błędne próby logowania, informując użytkownika o nieprawidłowych danych.

## 2. Routing widoku
- **Ścieżka:** `/login`
- **Dostęp:** Publiczny. Jeśli zalogowany użytkownik spróbuje uzyskać dostęp do tej ścieżki, powinien zostać przekierowany do swojego panelu głównego.

## 3. Struktura komponentów
Hierarchia komponentów dla widoku logowania będzie prosta i skoncentrowana na jednym zadaniu.

```
<LoginPage>
  <Card>
    <CardHeader>
      <CardTitle>Logowanie</CardTitle>
      <CardDescription>Zaloguj się, aby uzyskać dostęp.</CardDescription>
    </CardHeader>
    <CardContent>
      <LoginForm />
    </CardContent>
  </Card>
</LoginPage>
```

- **`LoginPage`**: Komponent-strona, który centruje zawartość i renderuje kartę logowania.
- **`LoginForm`**: Komponent zawierający właściwy formularz, pola do wprowadzania danych, walidację i przycisk do przesyłania.

## 4. Szczegóły komponentów
### `LoginPage`
- **Opis komponentu**: Główny kontener dla widoku `/login`. Odpowiada za układ strony i osadzenie formularza w estetycznym komponencie `Card` z biblioteki `shadcn/ui`. Komponent ten będzie również zarządzał logiką wywołania mutacji logowania i obsługą przekierowań po pomyślnym zalogowaniu.
- **Główne elementy**: `div` (jako kontener flex centrujący), `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`. Wewnątrz `CardContent` umieszczony zostanie komponent `LoginForm`.
- **Obsługiwane interakcje**: Komponent będzie nasłuchiwał na zdarzenie `submit` z `LoginForm`, aby zainicjować proces logowania.
- **Obsługiwana walidacja**: Brak walidacji na tym poziomie.
- **Typy**: Brak specyficznych typów DTO/ViewModel.
- **Propsy**: Brak.

### `LoginForm`
- **Opis komponentu**: Komponent implementujący interfejs formularza logowania przy użyciu `react-hook-form` do zarządzania stanem i `zod` do walidacji. Renderuje pola na nazwę użytkownika i hasło oraz przycisk "Zaloguj się". Wyświetla także komunikaty o błędach walidacji oraz błędy pochodzące z API.
- **Główne elementy**: Komponent `Form` z `shadcn/ui` (oparty o `react-hook-form`), `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage`, komponent `Input` dla nazwy użytkownika i hasła (z `type="password"` dla hasła), komponent `Button` do przesyłania formularza. Dodatkowo, komponent `Alert` do wyświetlania błędów API.
- **Obsługiwane interakcje**:
    - `onChange`: Aktualizacja stanu formularza przy wpisywaniu danych w pola.
    - `onSubmit`: Przesłanie danych formularza do komponentu nadrzędnego (`LoginPage`) w celu przetworzenia.
- **Obsługiwana walidacja**:
    - `username`: Pole wymagane. Musi być ciągiem znaków o długości co najmniej 5. Komunikat: "Nazwa użytkownika jest wymagana."
    - `password`: Pole wymagane. Musi być ciągiem znaków o długości co najmniej 5. Komunikat: "Hasło jest wymagane."
- **Typy**: `LoginFormData`
- **Propsy**:
    - `onSubmit: (data: LoginFormData) => void`: Funkcja zwrotna wywoływana z danymi formularza po pomyślnej walidacji.
    - `isLoading: boolean`: Informuje formularz, czy trwa proces logowania (do zablokowania przycisku).
    - `error: string | null`: Komunikat o błędzie z API do wyświetlenia.

## 5. Typy

### DTO (Data Transfer Object) - dane z API
```typescript
// Odpowiedź z POST /api/v1/auth/token
interface TokenDTO {
  access_token: string;
  token_type: 'bearer';
}

// Odpowiedź z GET /api/v1/users/me
interface UserDTO {
  id: number;
  username: string;
  role: 'admin' | 'student';
  is_active: boolean;
  created_at: string; // ISO Date String
}
```

### ViewModel - dane dla widoku
```typescript
// Struktura danych formularza logowania
interface LoginFormData {
  username: string;
  password: string;
}
```

## 6. Zarządzanie stanem
Zarządzanie stanem zostanie podzielone na trzy poziomy:

1.  **Stan formularza (lokalny)**: Zarządzany przez `react-hook-form` w komponencie `LoginForm`. Obejmuje wartości pól, status walidacji i stan przesyłania.
2.  **Stan asynchroniczny (strony)**: Zarządzany w `LoginPage` za pomocą hooka `useMutation` z biblioteki `TanStack Query`. Obejmuje:
    - `isPending` (`isLoading`): Status ładowania podczas komunikacji z API.
    - `error`: Obiekt błędu zwrócony przez API.
3.  **Stan globalny (aplikacji)**: Zarządzany przez `React Context` (`AuthContext`). Po pomyślnym zalogowaniu, token JWT oraz dane użytkownika (`UserDTO`) zostaną zapisane w kontekście i `localStorage`, aby były dostępne w całej aplikacji do uwierzytelniania zapytań i personalizacji interfejsu. Potrzebny będzie hook `useAuth` do interakcji z tym kontekstem.

## 7. Integracja API
Proces logowania wymaga dwóch kolejnych wywołań API, które zostaną zorkiestrowane w ramach jednej mutacji `TanStack Query`.

1.  **Zapytanie o token (Authentication)**:
    -   **Endpoint**: `POST /api/v1/auth/token`
    -   **Metoda**: `POST`
    -   **Typ zawartości**: `application/x-www-form-urlencoded`
    -   **Ciało żądania**: `username={username}&password={password}`
    -   **Odpowiedź sukcesu (200 OK)**: `TokenDTO` (`{ access_token, token_type }`)
    -   **Odpowiedź błędu (401 Unauthorized)**: Błąd informujący o niepoprawnych danych.

2.  **Zapytanie o dane użytkownika (Authorization)**:
    -   **Endpoint**: `GET /api/v1/users/me`
    -   **Metoda**: `GET`
    -   **Nagłówek autoryzacji**: `Authorization: Bearer <access_token>` (token z poprzedniego zapytania)
    -   **Odpowiedź sukcesu (200 OK)**: `UserDTO` (`{ id, username, role, ... }`)
    -   **Odpowiedź błędu (401 Unauthorized)**: Błąd w przypadku nieprawidłowego tokenu.

Logika ta zostanie opakowana w funkcji `mutationFn` hooka `useMutation`.

## 8. Interakcje użytkownika
- **Wpisywanie danych**: Użytkownik wpisuje nazwę użytkownika i hasło. Pola są aktualizowane, a hasło jest maskowane.
- **Próba wysłania pustego formularza**: Użytkownik klika "Zaloguj się" bez wypełniania pól. Pod polami pojawiają się komunikaty o błędach walidacji. Żądanie API nie jest wysyłane.
- **Wysłanie poprawnych danych**: Użytkownik klika "Zaloguj się" po wypełnieniu formularza.
    - Przycisk "Zaloguj się" staje się nieaktywny, a na nim może pojawić się ikona ładowania.
    - Rozpoczyna się mutacja (wywołanie API).
    - **W przypadku sukcesu**: Token i dane użytkownika są zapisywane w stanie globalnym, a użytkownik jest przekierowywany na odpowiedni pulpit (`/admin/dashboard` lub `/student/dashboard`).
    - **W przypadku błędu**: Przycisk staje się ponownie aktywny, a na ekranie pojawia się komunikat o błędzie (np. "Nieprawidłowa nazwa użytkownika lub hasło.").

## 9. Warunki i walidacja
- **Walidacja po stronie klienta**: `LoginForm` wykorzysta bibliotekę `zod` do zdefiniowania schematu walidacji, który sprawdzi, czy pola `username` i `password` nie są puste przed wysłaniem formularza. `react-hook-form` zintegruje się z tym schematem i automatycznie wyświetli błędy.
- **Wpływ na interfejs**:
    - Jeśli walidacja nie przejdzie pomyślnie, przycisk `submit` nie uruchomi logiki logowania, a pod odpowiednimi polami pojawią się komunikaty o błędach.
    - Podczas oczekiwania na odpowiedź API (`isLoading`), formularz i przycisk zostaną zablokowane, aby zapobiec wielokrotnemu przesyłaniu.

## 10. Obsługa błędów
- **Nieprawidłowe dane logowania**: API zwróci status `401`. Należy przechwycić ten błąd i wyświetlić w komponencie `Alert` ogólny komunikat, np.: `Nieprawidłowa nazwa użytkownika lub hasło.`. Nie należy ujawniać, które pole jest niepoprawne.
- **Błąd serwera/sieci**: W przypadku błędów `5xx` lub problemów z połączeniem sieciowym, należy wyświetlić generyczny komunikat, np.: `Wystąpił nieoczekiwany błąd. Spróbuj ponownie później.`.
- **Błąd w drugim kroku (pobieranie użytkownika)**: Jeśli uzyskanie tokenu się powiedzie, ale pobranie danych użytkownika nie, proces logowania należy uznać za nieudany. Należy wyświetlić ogólny błąd logowania i nie zapisywać tokenu.

## 11. Kroki implementacji
1.  **Utworzenie plików**: Stworzyć pliki dla komponentów: `src/pages/LoginPage.tsx` oraz `src/components/auth/LoginForm.tsx`.
2.  **Definicja typów i schematu walidacji**: W osobnym pliku (`src/types/auth.ts`) lub bezpośrednio w komponentach zdefiniować interfejsy `TokenDTO`, `UserDTO`, `LoginFormData` oraz schemat `zod` dla formularza.
3.  **Implementacja `LoginForm`**:
    -   Zbudować formularz przy użyciu `react-hook-form` i komponentów `shadcn/ui` (`Form`, `Input`, `Button`).
    -   Podłączyć schemat walidacji `zod`.
    -   Dodać propsy `onSubmit`, `isLoading` i `error` do sterowania zachowaniem formularza z zewnątrz.
    -   Dodać `Alert` do wyświetlania błędu.
4.  **Implementacja `LoginPage`**:
    -   Stworzyć układ strony, centrując komponent `Card`.
    -   Zaimplementować logikę `useMutation` z `TanStack Query` do obsługi dwuetapowego procesu logowania.
        -   Pamiętać o użyciu `URLSearchParams` do skonstruowania ciała żądania dla endpointu `/token`.
    -   W `onSuccess` mutacji, zapisać dane w `AuthContext` i przekierować użytkownika za pomocą `useNavigate` z `react-router-dom`.
    -   W `onError`, przekazać komunikat o błędzie do `LoginForm`.
5.  **Konfiguracja `AuthContext`**:
    -   Stworzyć `AuthProvider`, który będzie zarządzał stanem `token` i `user`.
    -   Zaimplementować w nim funkcję `login`, która będzie wywoływana przez `LoginPage`.
    -   Opakować całą aplikację w `AuthProvider` w głównym pliku `App.tsx`.
6.  **Routing**: W głównym pliku konfiguracyjnym routera (`src/App.tsx` lub dedykowany plik) dodać publiczną trasę `/login` wskazującą na `LoginPage`.
7.  **Testowanie**: Przetestować wszystkie ścieżki: pomyślne logowanie dla admina i studenta, błędne dane, błędy walidacji i błędy serwera. 