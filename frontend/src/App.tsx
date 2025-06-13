import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './lib/auth-context';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { StudentDashboard } from './pages/student/StudentDashboard';
import './App.css';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Admin routes */}
            <Route path="/admin" element={<ProtectedRoute requiredRole="admin" />}>
              <Route path="dashboard" element={<AdminDashboard />} />
              {/* Add more admin routes here */}
            </Route>
            
            {/* Student routes */}
            <Route path="/student" element={<ProtectedRoute requiredRole="student" />}>
              <Route path="dashboard" element={<StudentDashboard />} />
              {/* Add more student routes here */}
            </Route>
            
            {/* Redirect root to login */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            
            {/* Catch all other routes */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
