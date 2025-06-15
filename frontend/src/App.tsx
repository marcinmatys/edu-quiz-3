import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './lib/auth-context';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import AdminQuizzesPage from './pages/admin/AdminQuizzesPage';
import { StudentDashboard } from './pages/student/StudentDashboard';
import { StudentQuizzesPage } from './pages/student/StudentQuizzesPage';
import { AdminLayoutRoute } from './components/layout/AdminLayoutRoute';
import { StudentLayoutRoute } from './components/layout/StudentLayoutRoute';
import { QuizTakePage } from './pages/student/QuizTakePage';
import { QuizSummaryPage } from './pages/student/QuizSummaryPage';
import { Toaster } from './components/ui/toaster';
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
              <Route element={<AdminLayoutRoute />}>
                <Route path="dashboard" element={<AdminDashboard />} />
                <Route path="quizzes" element={<AdminQuizzesPage />} />
                {/* Add more admin routes here */}
              </Route>
            </Route>
            
            {/* Student routes */}
            <Route path="/student" element={<ProtectedRoute requiredRole="student" />}>
              <Route element={<StudentLayoutRoute />}>
                <Route path="dashboard" element={<StudentDashboard />} />
                <Route path="quizzes" element={<StudentQuizzesPage />} />
                <Route path="quiz/:quizId" element={<QuizTakePage />} />
                <Route path="quiz/:quizId/summary" element={<QuizSummaryPage />} />
                {/* Add more student routes here */}
              </Route>
            </Route>
            
            {/* Redirect root to login */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            
            {/* Catch all other routes */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
          <Toaster />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
