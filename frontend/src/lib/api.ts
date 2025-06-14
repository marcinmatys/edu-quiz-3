/**
 * API utility functions for making authenticated requests
 */
import type { UserDTO } from "../types/auth";

// API configuration

// Configuration for API endpoints
// Set this to your real API base URL when needed (e.g., 'https://api.example.com')
// Leave empty to use relative URLs (which will be intercepted by MSW when mocking is enabled)
export const API_BASE_URL = '/api/v1';

/**
 * Get the authentication token from localStorage
 */
const getToken = (): string | null => {
  return localStorage.getItem('token');
};

/**
 * Create headers with authentication token
 */
const createHeaders = (contentType = 'application/json'): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': contentType,
  };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

/**
 * Handle API response
 */
const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    if (response.status === 401) {
      // Clear auth data on unauthorized
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Force page reload to reset application state
      window.location.href = '/login';
      throw new Error('Sesja wygasła. Zaloguj się ponownie.');
    }
    
    // Try to get error message from response
    try {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Wystąpił błąd podczas komunikacji z serwerem.');
    } catch (e) {
      throw new Error(`Błąd ${response.status}: ${response.statusText}`);
    }
  }
  
  // Return parsed JSON or empty object if no content
  if (response.status === 204) {
    return {} as T;
  }
  
  return response.json();
};

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface LoginResponse {
  token: string;
  user: UserDTO;
}

// Helper function for API calls
export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = API_BASE_URL ? `${API_BASE_URL}${endpoint}` : endpoint;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  // For non-JSON responses or empty responses
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return null;
  }

  return response.json();
};

/**
 * API client for making authenticated requests
 */
export const api = {
  /**
   * GET request
   */
  get: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: createHeaders(),
    });
    
    return handleResponse<T>(response);
  },
  
  /**
   * POST request
   */
  post: async <T>(endpoint: string, data?: any): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: createHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });
    
    return handleResponse<T>(response);
  },
  
  /**
   * PUT request
   */
  put: async <T>(endpoint: string, data: any): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: createHeaders(),
      body: JSON.stringify(data),
    });
    
    return handleResponse<T>(response);
  },
  
  /**
   * DELETE request
   */
  delete: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: createHeaders(),
    });
    
    return handleResponse<T>(response);
  },
  
  /**
   * Form data POST request (for file uploads or form submissions)
   */
  postFormData: async <T>(endpoint: string, formData: FormData): Promise<T> => {
    const headers: HeadersInit = {};
    
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    return handleResponse<T>(response);
  },
  
  /**
   * Special method for login (doesn't use auth token)
   */
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const tokenResponse = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    const tokenData = await handleResponse<TokenResponse>(tokenResponse);
    
    // Get user data with token
    const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
      headers: {
        Authorization: `Bearer ${tokenData.access_token}`,
      },
    });
    
    const userData = await handleResponse<UserDTO>(userResponse);
    
    return {
      token: tokenData.access_token,
      user: userData,
    };
  },
}; 