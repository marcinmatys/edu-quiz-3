import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { useNavigate } from "react-router-dom";

export function StudentDashboard() {
  const navigate = useNavigate();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Panel ucznia</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Dostępne quizy</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col space-y-4">
            <p>Przeglądaj i rozwiązuj dostępne quizy.</p>
            <Button 
              onClick={() => navigate("/student/quizzes")}
              className="mt-auto"
            >
              Przejdź do quizów
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Moje wyniki</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Sprawdź swoje wyniki z rozwiązanych quizów.</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Profil</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Zarządzaj swoim profilem.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 