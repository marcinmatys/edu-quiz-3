import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { handlers } from '../mocks/handlers';
import { LoginPage } from './LoginPage';
import { AuthProvider } from '../lib/auth-context';

// Setup mock server
const server = setupServer(...handlers);

// Setup before and after hooks
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Mock navigate function
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('LoginPage', () => {
  // Helper function to render the component with all providers
  const renderLoginPage = () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    return render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <MemoryRouter>
            <LoginPage />
          </MemoryRouter>
        </AuthProvider>
      </QueryClientProvider>
    );
  };

  it('renders login form correctly', () => {
    renderLoginPage();
    
    expect(screen.getByText('Logowanie')).toBeInTheDocument();
    expect(screen.getByText('Zaloguj się, aby uzyskać dostęp.')).toBeInTheDocument();
    expect(screen.getByLabelText('Nazwa użytkownika')).toBeInTheDocument();
    expect(screen.getByLabelText('Hasło')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Zaloguj się' })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    renderLoginPage();
    
    // Submit form without filling fields
    fireEvent.click(screen.getByRole('button', { name: 'Zaloguj się' }));
    
    // Wait for validation errors
    await waitFor(() => {
      expect(screen.getByText('Nazwa użytkownika jest wymagana.')).toBeInTheDocument();
      expect(screen.getByText('Hasło jest wymagane.')).toBeInTheDocument();
    });
  });

  it('successfully logs in as admin and redirects', async () => {
    renderLoginPage();
    
    // Fill form with admin credentials
    fireEvent.change(screen.getByLabelText('Nazwa użytkownika'), { target: { value: 'admin' } });
    fireEvent.change(screen.getByLabelText('Hasło'), { target: { value: 'admin123' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: 'Zaloguj się' }));
    
    // Wait for redirect
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/admin/dashboard', expect.anything());
    });
  });

  it('successfully logs in as student and redirects', async () => {
    renderLoginPage();
    
    // Fill form with student credentials
    fireEvent.change(screen.getByLabelText('Nazwa użytkownika'), { target: { value: 'student' } });
    fireEvent.change(screen.getByLabelText('Hasło'), { target: { value: 'student123' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: 'Zaloguj się' }));
    
    // Wait for redirect
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/student/dashboard', expect.anything());
    });
  });

  it('shows error message for invalid credentials', async () => {
    renderLoginPage();
    
    // Fill form with invalid credentials
    fireEvent.change(screen.getByLabelText('Nazwa użytkownika'), { target: { value: 'invalid' } });
    fireEvent.change(screen.getByLabelText('Hasło'), { target: { value: 'wrong' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: 'Zaloguj się' }));
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Nieprawidłowa nazwa użytkownika lub hasło.')).toBeInTheDocument();
    });
  });
}); 