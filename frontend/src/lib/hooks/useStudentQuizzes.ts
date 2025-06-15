import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api';
import type { 
  QuizListItemDto, 
  QuizCardViewModel, 
  SortParams,
  LevelDto
} from '../../types/quiz';

/**
 * Custom hook for managing student quizzes
 * Handles fetching, sorting, and transforming quiz data
 */
export function useStudentQuizzes() {
  // Local state for sort parameters
  const [sortParams, setSortParams] = useState<SortParams>({
    sortBy: 'level',
    order: 'asc'
  });

  // Fetch levels for mapping level_id to descriptions
  const levelsQuery = useQuery({
    queryKey: ['levels'],
    queryFn: () => api.get<LevelDto[]>('/levels/')
  });

  // Fetch quizzes with sort parameters
  const quizzesQuery = useQuery({
    queryKey: ['studentQuizzes', sortParams],
    queryFn: async () => {
      const queryParams = new URLSearchParams({
        sort_by: sortParams.sortBy,
        order: sortParams.order
      });
      return api.get<QuizListItemDto[]>(`/quizzes/?${queryParams}`);
    }
  });

  // Transform DTO to ViewModel
  const transformQuizzes = (quizzes: QuizListItemDto[]): QuizCardViewModel[] => {
    if (!levelsQuery.data) return [];
    
    return quizzes.map(quiz => {
      // Find level description
      const level = levelsQuery.data.find(l => l.id === quiz.level_id);
      const levelDescription = level ? level.description : `Poziom ${quiz.level_id}`;
      
      // Format question count text
      const questionCountText = `Liczba pytań: ${quiz.question_count}`;
      
      // Format last result text if available
      let lastResultText = null;
      if (quiz.last_result) {
        lastResultText = `Ostatni wynik: ${quiz.last_result.score}/${quiz.last_result.max_score}`;
      }
      
      // Create path for starting the quiz
      const startQuizPath = `/student/quiz/${quiz.id}`;
      
      return {
        id: quiz.id,
        title: quiz.title,
        levelDescription,
        questionCountText,
        lastResultText,
        startQuizPath
      };
    });
  };

  // Derived state
  const quizzes = quizzesQuery.data && levelsQuery.data 
    ? transformQuizzes(quizzesQuery.data) 
    : [];
  
  // Combined loading state
  const isLoading = quizzesQuery.isLoading || levelsQuery.isLoading;
  
  // Combined error state
  const error = quizzesQuery.error || levelsQuery.error;

  return {
    quizzes,
    isLoading,
    error,
    sortParams,
    setSortParams
  };
} 