import { AdminLayout } from "../../components/layout/AdminLayout";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";

export function AdminDashboard() {
  return (
    <AdminLayout>
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Panel administratora</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Quizy</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Zarządzaj quizami i pytaniami.</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Użytkownicy</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Zarządzaj kontami użytkowników.</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Wyniki</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Przeglądaj wyniki uczniów.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AdminLayout>
  );
} 