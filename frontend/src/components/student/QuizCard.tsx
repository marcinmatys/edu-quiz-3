import { useNavigate } from "react-router-dom";
import { 
  Card, 
  CardContent, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import type { QuizCardViewModel } from "../../types/quiz";

interface QuizCardProps {
  quiz: QuizCardViewModel;
}

/**
 * Component that displays a single quiz card in the student view
 */
export function QuizCard({ quiz }: QuizCardProps) {
  const navigate = useNavigate();
  
  // Handle start quiz button click
  const handleStartQuiz = () => {
    navigate(quiz.startQuizPath);
  };
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="text-xl">{quiz.title}</CardTitle>
        <div className="text-sm text-muted-foreground">{quiz.levelDescription}</div>
      </CardHeader>
      
      <CardContent className="flex-grow">
        <div className="space-y-2">
          <p className="text-sm">{quiz.questionCountText}</p>
          
          {quiz.lastResultText && (
            <Badge variant="outline" className="bg-muted">
              {quiz.lastResultText}
            </Badge>
          )}
        </div>
      </CardContent>
      
      <CardFooter>
        <Button onClick={handleStartQuiz} className="w-full">
          Rozpocznij
        </Button>
      </CardFooter>
    </Card>
  );
} 