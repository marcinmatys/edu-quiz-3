import { StudentLayout } from "../../components/layout/StudentLayout";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";

export function StudentDashboard() {
  return (
    <StudentLayout>
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Panel ucznia</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Dostępne quizy</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Przeglądaj i rozwiązuj dostępne quizy.</p>
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
    </StudentLayout>
  );
} 