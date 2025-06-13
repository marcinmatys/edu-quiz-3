import { useNavigate } from 'react-router-dom';
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
        <div className="font-bold text-xl">EduQuiz</div>
        
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