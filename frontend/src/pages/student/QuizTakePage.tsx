import { useParams } from "react-router-dom";
import { useQuizEngine } from "../../lib/hooks/useQuizEngine";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { Spinner } from "../../components/ui/spinner";

// Component for displaying a single answer option
const AnswerOption = ({
  answer,
  onClick,
  disabled,
}: {
  answer: { id: number; text: string; status: string };
  onClick: (answerId: number) => void;
  disabled: boolean;
}) => {
  // Define styles based on answer status
  const getButtonVariant = () => {
    switch (answer.status) {
      case "correct":
        return "default" as const;
      case "incorrect":
        return "destructive" as const;
      case "selected":
        return "secondary" as const;
      default:
        return "outline" as const;
    }
  };

  // Add additional class for correct answers
  const getAdditionalClasses = () => {
    if (answer.status === "correct") {
      return "bg-green-100 hover:bg-green-200 text-green-900 border-green-500";
    }
    return "";
  };

  return (
    <Button
      variant={getButtonVariant()}
      className={`w-full justify-start text-left mb-2 h-auto py-3 ${getAdditionalClasses()}`}
      onClick={() => onClick(answer.id)}
      disabled={disabled}
    >
      {answer.text}
    </Button>
  );
};

// Component for displaying the question and answers
const QuizDisplay = ({
  question,
  answerStates,
  progress,
  onAnswerSelect,
  isAnswerChecked,
}: {
  question: { id: number; text: string };
  answerStates: { id: number; text: string; status: string }[];
  progress: { current: number; total: number };
  onAnswerSelect: (answerId: number) => void;
  isAnswerChecked: boolean;
}) => {
  return (
    <Card className="w-full max-w-3xl">
      <CardHeader>
        <div className="flex justify-between items-center mb-2">
          <CardTitle>Pytanie {progress.current} z {progress.total}</CardTitle>
          <div className="text-sm text-muted-foreground">
            Postęp: {progress.current}/{progress.total}
          </div>
        </div>
        <div className="w-full bg-secondary h-2 rounded-full">
          <div
            className="bg-primary h-2 rounded-full"
            style={{ width: `${(progress.current / progress.total) * 100}%` }}
          ></div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-6 text-lg font-medium">{question.text}</div>
        <div>
          {answerStates.map((answer) => (
            <AnswerOption
              key={answer.id}
              answer={answer}
              onClick={onAnswerSelect}
              disabled={isAnswerChecked}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Component for displaying feedback after answering
const FeedbackDisplay = ({ feedback }: { feedback: string | null }) => {
  if (!feedback) return null;

  return (
    <Alert className="mt-4 max-w-3xl">
      <AlertDescription>{feedback}</AlertDescription>
    </Alert>
  );
};

// Component for quiz navigation controls
const QuizControls = ({
  onNext,
  isNextDisabled,
  isLastQuestion,
}: {
  onNext: () => void;
  isNextDisabled: boolean;
  isLastQuestion: boolean;
}) => {
  return (
    <div className="mt-4 flex justify-end max-w-3xl">
      <Button onClick={onNext} disabled={isNextDisabled}>
        {isLastQuestion ? "Zakończ quiz" : "Następne pytanie"}
      </Button>
    </div>
  );
};

// Component for displaying error state with retry option
const ErrorState = ({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) => {
  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-center text-destructive">Błąd</CardTitle>
      </CardHeader>
      <CardContent className="text-center">
        <p className="mb-4">{message}</p>
        <Button onClick={onRetry}>Spróbuj ponownie</Button>
      </CardContent>
    </Card>
  );
};

// Main quiz taking page component
export const QuizTakePage = () => {
  const { quizId } = useParams<{ quizId: string }>();
  
  if (!quizId) {
    return <div>Nieprawidłowy identyfikator quizu</div>;
  }

  const {
    quizData,
    isLoadingQuiz,
    errorMessage,
    currentQuestion,
    answerStates,
    feedback,
    isFinished,
    progress,
    handleAnswerSelect,
    handleNext,
    retryLoading,
    isAnswerChecked,
    isNextDisabled,
  } = useQuizEngine(quizId);

  if (isLoadingQuiz) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-200px)]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (errorMessage || !quizData || !currentQuestion) {
    return (
      <div className="container mx-auto py-8 px-4 flex justify-center">
        <ErrorState 
          message={errorMessage || "Nie można załadować quizu. Spróbuj ponownie później."} 
          onRetry={retryLoading}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">{quizData.title}</h1>
      <div className="flex flex-col items-center">
        <QuizDisplay
          question={currentQuestion}
          answerStates={answerStates}
          progress={progress}
          onAnswerSelect={handleAnswerSelect}
          isAnswerChecked={isAnswerChecked}
        />
        <FeedbackDisplay feedback={feedback} />
        <QuizControls
          onNext={handleNext}
          isNextDisabled={isNextDisabled}
          isLastQuestion={isFinished}
        />
      </div>
    </div>
  );
}; 