import { Alert, AlertDescription, AlertTitle } from "../../components/ui/alert";
import { QuizList } from "../../components/student/QuizList";
import { QuizListControls } from "../../components/student/QuizListControls";
import { useStudentQuizzes } from "../../lib/hooks/useStudentQuizzes";

/**
 * Main page component for the student quizzes view
 * Shows a list of available quizzes that the student can take
 */
export function StudentQuizzesPage() {
  // Use the custom hook to manage quizzes data and state
  const { quizzes, isLoading, error, sortParams, setSortParams } = useStudentQuizzes();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dostępne quizy</h1>
        <p className="text-muted-foreground">
          Przeglądaj i rozwiązuj dostępne quizy edukacyjne.
        </p>
      </div>

      {/* Error state */}
      {error && (
        <Alert variant="destructive">
          <AlertTitle>Wystąpił błąd</AlertTitle>
          <AlertDescription>
            Nie udało się załadować listy quizów. Spróbuj odświeżyć stronę.
          </AlertDescription>
        </Alert>
      )}

      {/* Sort controls */}
      <QuizListControls 
        sortParams={sortParams} 
        onSortChange={setSortParams} 
      />

      {/* Quiz list */}
      <QuizList 
        quizzes={quizzes} 
        isLoading={isLoading} 
      />
    </div>
  );
} 