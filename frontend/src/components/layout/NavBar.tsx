import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../ui/button';
import { useAuth } from '../../lib/auth-context';

export function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-slate-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center gap-6">
          <Link to={user?.role === 'admin' ? '/admin/dashboard' : '/student/dashboard'} className="font-bold text-xl">
            EduQuiz
          </Link>
          
          {user?.role === 'admin' && (
            <div className="flex items-center gap-4">
              <Link to="/admin/dashboard" className="text-sm hover:text-slate-300">
                Dashboard
              </Link>
              <Link to="/admin/quizzes" className="text-sm hover:text-slate-300">
                Quizy
              </Link>
              <Link to="/admin/users" className="text-sm hover:text-slate-300">
                Użytkownicy
              </Link>
              <Link to="/admin/results" className="text-sm hover:text-slate-300">
                Wyniki
              </Link>
            </div>
          )}
          
          {user?.role === 'student' && (
            <div className="flex items-center gap-4">
              <Link to="/student/dashboard" className="text-sm hover:text-slate-300">
                Dashboard
              </Link>
              <Link to="/student/quizzes" className="text-sm hover:text-slate-300">
                Quizy
              </Link>
              <Link to="/student/results" className="text-sm hover:text-slate-300">
                Moje wyniki
              </Link>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-4">
          {user && (
            <>
              <span className="text-sm">
                Zalogowany jako: <strong>{user.username}</strong> ({user.role})
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Wyloguj
              </Button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
} 