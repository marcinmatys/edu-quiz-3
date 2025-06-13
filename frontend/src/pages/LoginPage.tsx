import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate, useLocation } from "react-router-dom";
import { LoginForm } from "../components/auth/LoginForm";
import type { LoginFormData, TokenDTO, UserDTO } from "../types/auth";
import { useAuth } from "../lib/auth-context";
import { api } from "../lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";

interface LoginResponse {
  token: string;
  user: UserDTO;
}

interface LocationState {
  from?: {
    pathname: string;
  };
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  
  // Get the redirect path from location state
  const state = location.state as LocationState;
  const from = state?.from?.pathname || (user?.role === "admin" ? "/admin/dashboard" : "/student/dashboard");

  // Redirect if user is already logged in
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, user, navigate, from]);

  // Define the login mutation
  const loginMutation = useMutation<LoginResponse, Error, LoginFormData>({
    mutationFn: async (formData: LoginFormData) => {
      return api.login(formData.username, formData.password);
    },
    onSuccess: (data: LoginResponse) => {
      login(data.token, data.user);
      // Redirect to the original URL or dashboard based on role
      navigate(from, { replace: true });
    },
    onError: (error: Error) => {
      setError(error.message);
    },
  });

  const handleSubmit = (formData: LoginFormData) => {
    setError(null);
    loginMutation.mutate(formData);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Logowanie</CardTitle>
          <CardDescription>Zaloguj się, aby uzyskać dostęp.</CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm
            onSubmit={handleSubmit}
            isLoading={loginMutation.isPending}
            error={error}
          />
        </CardContent>
      </Card>
    </div>
  );
} 