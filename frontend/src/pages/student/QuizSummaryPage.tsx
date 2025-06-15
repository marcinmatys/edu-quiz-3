import { useEffect } from "react";
import { useLocation, useNavigate, Navigate } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "../../components/ui/card";
import { showWarningToast } from "../../lib/toast-utils";

// Component for displaying quiz results summary
const SummaryCard = ({
  score,
  maxScore,
  onReturn,
}: {
  score: number;
  maxScore: number;
  onReturn: () => void;
}) => {
  // Calculate percentage for visual feedback
  const percentage = Math.round((score / maxScore) * 100);
  
  // Determine feedback message based on score percentage
  const getFeedbackMessage = () => {
    if (percentage >= 90) return "Znakomity wynik!";
    if (percentage >= 75) return "Bardzo dobry wynik!";
    if (percentage >= 60) return "Dobry wynik!";
    if (percentage >= 40) return "Możesz poprawić swój wynik.";
    return "Spróbuj ponownie, aby poprawić swój wynik.";
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-center">Podsumowanie quizu</CardTitle>
      </CardHeader>
      <CardContent className="text-center">
        <div className="text-6xl font-bold mb-4">
          {score}/{maxScore}
        </div>
        <div className="text-2xl mb-2">{percentage}%</div>
        <p className="text-muted-foreground">{getFeedbackMessage()}</p>
      </CardContent>
      <CardFooter className="flex justify-center">
        <Button onClick={onReturn}>Wróć do listy quizów</Button>
      </CardFooter>
    </Card>
  );
};

// Main quiz summary page component
export const QuizSummaryPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Check if we have the required data in location state
  const score = location.state?.score;
  const maxScore = location.state?.maxScore;
  
  useEffect(() => {
    // Show warning if trying to access summary page directly
    if (score === undefined || maxScore === undefined) {
      showWarningToast("Brak danych o wyniku quizu. Przekierowanie do listy quizów.");
    }
  }, [score, maxScore]);
  
  // If no score data is available, redirect to quizzes list
  if (score === undefined || maxScore === undefined) {
    return <Navigate to="/student/quizzes" replace />;
  }
  
  // Handler for returning to quizzes list
  const handleReturn = () => {
    navigate("/student/quizzes");
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex justify-center">
        <SummaryCard score={score} maxScore={maxScore} onReturn={handleReturn} />
      </div>
    </div>
  );
}; 