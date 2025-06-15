import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { showErrorToast, formatErrorMessage } from "../toast-utils";
import type {
  AnswerCheckRequestDto,
  AnswerCheckResponseDto,
  AnswerStateViewModel,
  QuizReadDetailStudentDto,
  ResultCreateDto,
  AnswerStatus,
  AnswerReadStudentDto,
} from "../../types/quiz";

/**
 * Custom hook for managing quiz taking logic
 */
export const useQuizEngine = (quizId: string) => {
  const navigate = useNavigate();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [checkedAnswerInfo, setCheckedAnswerInfo] = useState<AnswerCheckResponseDto | null>(null);
  const [selectedAnswerId, setSelectedAnswerId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch quiz data
  const quizQuery = useQuery({
    queryKey: ["quiz", quizId],
    queryFn: async () => {
      try {
        return await api.get<QuizReadDetailStudentDto>(`/quizzes/${quizId}`);
      } catch (error) {
        const message = formatErrorMessage(error);
        setErrorMessage(message);
        showErrorToast(`Nie można załadować quizu: ${message}`);
        throw error;
      }
    },
    retry: 1, // Retry once before showing error
  });

  // Mutation for checking answers
  const checkAnswerMutation = useMutation({
    mutationFn: async (data: AnswerCheckRequestDto) => {
      try {
        return await api.post<AnswerCheckResponseDto>(`/quizzes/${quizId}/check-answer`, data);
      } catch (error) {
        const message = formatErrorMessage(error);
        showErrorToast(`Błąd sprawdzania odpowiedzi: ${message}`);
        throw error;
      }
    },
    onSuccess: (data) => {
      setCheckedAnswerInfo(data);
      if (data.is_correct) {
        setScore((prev) => prev + 1);
      }
      setErrorMessage(null);
    },
    onError: () => {
      // Allow user to try again
      setSelectedAnswerId(null);
    },
  });

  // Mutation for submitting quiz results
  const submitResultMutation = useMutation({
    mutationFn: async (data: ResultCreateDto) => {
      try {
        return await api.post<void>(`/quizzes/${quizId}/results`, data);
      } catch (error) {
        const message = formatErrorMessage(error);
        showErrorToast(`Nie można zapisać wyników: ${message}`);
        throw error;
      }
    },
    onSuccess: () => {
      // Navigate to summary page with score data
      navigate(`/student/quiz/${quizId}/summary`, {
        state: {
          score,
          maxScore: quizQuery.data?.questions?.length || 0,
        },
      });
      setErrorMessage(null);
    },
  });

  // Get current question
  const currentQuestion = quizQuery.data?.questions?.[currentQuestionIndex];

  // Calculate answer states for UI
  const answerStates: AnswerStateViewModel[] = currentQuestion?.answers.map((answer: AnswerReadStudentDto) => {
    let status: AnswerStatus = "default";

    if (selectedAnswerId === answer.id) {
      status = "selected";
    }

    if (checkedAnswerInfo) {
      if (answer.id === checkedAnswerInfo.correct_answer_id) {
        status = "correct";
      } else if (selectedAnswerId === answer.id && !checkedAnswerInfo.is_correct) {
        status = "incorrect";
      }
    }

    return {
      id: answer.id,
      text: answer.text,
      status,
    };
  }) || [];

  // Handle answer selection
  const handleAnswerSelect = (answerId: number) => {
    if (checkedAnswerInfo) return; // Prevent selecting after answer is checked
    
    setSelectedAnswerId(answerId);
    
    if (!currentQuestion) return;
    
    checkAnswerMutation.mutate({
      question_id: currentQuestion.id,
      answer_id: answerId,
    });
  };

  // Handle next question or finish quiz
  const handleNext = () => {
    if (currentQuestionIndex < (quizQuery.data?.questions?.length || 0) - 1) {
      // Move to next question
      setCurrentQuestionIndex((prev) => prev + 1);
      setCheckedAnswerInfo(null);
      setSelectedAnswerId(null);
    } else {
      // Submit results
      submitResultMutation.mutate({
        score,
        max_score: quizQuery.data?.questions?.length || 0,
      });
    }
  };

  // Retry loading quiz data
  const retryLoading = () => {
    quizQuery.refetch();
  };

  // Calculate progress
  const progress = {
    current: currentQuestionIndex + 1,
    total: quizQuery.data?.questions?.length || 0,
  };

  return {
    quizData: quizQuery.data,
    isLoadingQuiz: quizQuery.isLoading,
    errorMessage,
    currentQuestion,
    answerStates,
    feedback: checkedAnswerInfo?.explanation || null,
    isSubmitting: checkAnswerMutation.isPending || submitResultMutation.isPending,
    isFinished: currentQuestionIndex >= (quizQuery.data?.questions?.length || 0) - 1,
    progress,
    handleAnswerSelect,
    handleNext,
    retryLoading,
    isAnswerChecked: !!checkedAnswerInfo,
    isNextDisabled: !checkedAnswerInfo,
  };
}; 