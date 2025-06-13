import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../lib/auth-context';
import type { ReactNode } from 'react';

interface ProtectedRouteProps {
  children?: ReactNode;
  requiredRole?: 'admin' | 'student';
  redirectPath?: string;
}

export function ProtectedRoute({ 
  children, 
  requiredRole,
  redirectPath = '/login' 
}: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  // If not authenticated, redirect to login with return URL
  if (!isAuthenticated) {
    return <Navigate to={redirectPath} state={{ from: location }} replace />;
  }

  // If role is required and user doesn't have it, redirect
  if (requiredRole && user?.role !== requiredRole) {
    // Redirect students trying to access admin pages to student dashboard
    // and vice versa
    const redirectTo = user?.role === 'admin' ? '/admin/dashboard' : '/student/dashboard';
    return <Navigate to={redirectTo} replace />;
  }

  // Render children if provided, otherwise render the Outlet
  return <>{children || <Outlet />}</>;
} 