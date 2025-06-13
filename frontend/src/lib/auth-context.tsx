import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import type { TokenDTO, UserDTO, AuthState } from "../types/auth";

interface AuthContextType extends AuthState {
  login: (token: string, user: UserDTO) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>(() => {
    // Initialize from localStorage if available
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    return {
      token: storedToken,
      user: storedUser ? JSON.parse(storedUser) : null,
      isAuthenticated: !!storedToken && !!storedUser
    };
  });

  // Login function to update context and localStorage
  const login = (token: string, user: UserDTO) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    setAuthState({
      token,
      user,
      isAuthenticated: true
    });
  };

  // Logout function to clear context and localStorage
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    setAuthState({
      token: null,
      user: null,
      isAuthenticated: false
    });
  };

  return (
    <AuthContext.Provider value={{ ...authState, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use the auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 