// Authentication Data Transfer Objects
export interface TokenDTO {
  access_token: string;
  token_type: 'bearer';
}

// User Data Transfer Object
export interface UserDTO {
  id: number;
  username: string;
  role: 'admin' | 'student';
  is_active: boolean;
  created_at: string; // ISO Date String
}

// Login Form Data
export interface LoginFormData {
  username: string;
  password: string;
}

// Auth Context State
export interface AuthState {
  token: string | null;
  user: UserDTO | null;
  isAuthenticated: boolean;
} 