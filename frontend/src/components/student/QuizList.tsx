import { Skeleton } from "../ui/skeleton";
import { QuizCard } from "./QuizCard";
import type { QuizCardViewModel } from "../../types/quiz";

interface QuizListProps {
  quizzes: QuizCardViewModel[];
  isLoading: boolean;
}

/**
 * Component that displays a grid of quiz cards
 * Shows loading skeletons when data is loading
 * Shows empty state message when there are no quizzes
 */
export function QuizList({ quizzes, isLoading }: QuizListProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, index) => (
          <QuizCardSkeleton key={index} />
        ))}
      </div>
    );
  }

  // Empty state
  if (quizzes.length === 0) {
    return <EmptyStateMessage />;
  }

  // Render quiz cards
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {quizzes.map((quiz) => (
        <QuizCard key={quiz.id} quiz={quiz} />
      ))}
    </div>
  );
}

/**
 * Loading skeleton for quiz cards
 */
function QuizCardSkeleton() {
  return (
    <div className="border rounded-lg p-4 h-full flex flex-col">
      <div className="space-y-2 mb-4">
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
      <div className="flex-grow space-y-2 mb-4">
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-6 w-1/4" />
      </div>
      <Skeleton className="h-10 w-full" />
    </div>
  );
}

/**
 * Message displayed when there are no quizzes
 */
function EmptyStateMessage() {
  return (
    <div className="text-center p-8 border rounded-lg bg-muted/50">
      <h3 className="text-lg font-medium mb-2">Brak dostępnych quizów</h3>
      <p className="text-muted-foreground">
        Obecnie nie ma żadnych opublikowanych quizów do rozwiązania.
        Sprawdź ponownie później.
      </p>
    </div>
  );
} 