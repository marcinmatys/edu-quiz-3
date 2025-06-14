import { useState, useCallback, useEffect, useMemo } from 'react';
import type { 
  QuizListItemDto, 
  QuizListItemVM, 
  QuizEditorVM, 
  CreateQuizRequestDto, 
  QuizUpdateDto,
  QuizFilters,
  QuestionDto
} from '../../types/quiz';
import { v4 as uuidv4 } from 'uuid';
import { api } from '../api'; // Import the API client

// Funkcja pomocnicza do konwersji DTO na ViewModel
const mapQuizDtoToVM = (quiz: QuizListItemDto, levelMap: Record<number, string>): QuizListItemVM => {
  return {
    ...quiz,
    level: levelMap[quiz.level_id] || `Poziom ${quiz.level_id}`
  };
};

// Funkcja pomocnicza do konwersji QuizEditorVM na QuizUpdateDto
const mapQuizVMToUpdateDto = (quiz: QuizEditorVM): QuizUpdateDto => {
  return {
    title: quiz.title,
    level_id: quiz.level_id,
    questions: quiz.questions.map(q => ({
      id: q.id,
      text: q.text,
      answers: q.answers.map(a => ({
        id: a.id,
        text: a.text,
        is_correct: a.is_correct
      }))
    }))
  };
};

export const useAdminQuizzes = () => {
  const [quizzes, setQuizzes] = useState<QuizListItemVM[]>([]);
  const [currentQuiz, setCurrentQuiz] = useState<QuizEditorVM | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [levelMap, setLevelMap] = useState<Record<number, string>>({});

  // Pobieranie poziomów (klas)
  const fetchLevels = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await api.get<Array<{ id: number, code: string }>>('/levels/');
      const map: Record<number, string> = {};
      data.forEach((level: { id: number, code: string }) => {
        map[level.id] = level.code;
      });
      setLevelMap(map);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Pobieranie listy quizów
  const fetchQuizzes = useCallback(async (filters: QuizFilters = {}) => {
    try {
      setIsLoading(true);
      setError(null);

      let endpoint = '/quizzes/';
      const queryParams = [];
      
      if (filters.status && filters.status !== 'all') {
        queryParams.push(`status=${filters.status}`);
      }
      
      if (queryParams.length > 0) {
        endpoint += `?${queryParams.join('&')}`;
      }

      const data = await api.get<QuizListItemDto[]>(endpoint);
      setQuizzes(data.map(quiz => mapQuizDtoToVM(quiz, levelMap)));
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
    } finally {
      setIsLoading(false);
    }
  }, [levelMap]);

  // Pobieranie pojedynczego quizu do edycji
  const selectQuizForEdit = useCallback(async (quizId: number) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Używamy istniejącego typu QuizListItemDto rozszerzonego o questions
      interface QuizDetailDto extends QuizListItemDto {
        questions: QuestionDto[];
      }
      
      const data = await api.get<QuizDetailDto>(`/quizzes/${quizId}`);
      
      // Konwersja danych z API do formatu QuizEditorVM
      const quizEditorVM: QuizEditorVM = {
        id: data.id,
        title: data.title,
        level_id: data.level_id,
        status: data.status,
        questions: data.questions.map((q) => ({
          id: q.id,
          uiId: uuidv4(),
          text: q.text,
          answers: q.answers.map((a) => ({
            id: a.id,
            uiId: uuidv4(),
            text: a.text,
            is_correct: a.is_correct
          }))
        }))
      };
      
      setCurrentQuiz(quizEditorVM);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Tworzenie nowego quizu przez AI
  const createNewQuiz = useCallback(async (data: CreateQuizRequestDto) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Używamy istniejącego typu QuizListItemDto rozszerzonego o questions
      interface GeneratedQuizDto extends QuizListItemDto {
        questions: QuestionDto[];
      }
      
      const responseData = await api.post<GeneratedQuizDto>('/quizzes/', data);
      
      // Konwersja danych z API do formatu QuizEditorVM
      const quizEditorVM: QuizEditorVM = {
        id: responseData.id,
        title: responseData.title,
        level_id: responseData.level_id,
        status: responseData.status,
        questions: responseData.questions.map((q) => ({
          id: q.id,
          uiId: uuidv4(),
          text: q.text,
          answers: q.answers.map((a) => ({
            id: a.id,
            uiId: uuidv4(),
            text: a.text,
            is_correct: a.is_correct
          }))
        }))
      };
      
      setCurrentQuiz(quizEditorVM);
      return quizEditorVM;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Zapisywanie quizu (jako wersja robocza)
  const saveQuiz = useCallback(async (quizData: QuizEditorVM) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const updateData: QuizUpdateDto = {
        ...mapQuizVMToUpdateDto(quizData),
        status: 'draft'
      };
      
      if (quizData.id) {
        await api.put(`/quizzes/${quizData.id}`, updateData);
      } else {
        await api.post('/quizzes', updateData);
      }
      
      // Odświeżamy listę quizów
      await fetchQuizzes();
      
      // Czyścimy aktualnie edytowany quiz
      setCurrentQuiz(null);
      
      return true;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [fetchQuizzes]);

  // Publikowanie quizu
  const publishQuiz = useCallback(async (quizData: QuizEditorVM) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const updateData: QuizUpdateDto = {
        ...mapQuizVMToUpdateDto(quizData),
        status: 'published'
      };
      
      if (quizData.id) {
        await api.put(`/quizzes/${quizData.id}`, updateData);
      } else {
        await api.post('/quizzes', updateData);
      }
      
      // Odświeżamy listę quizów
      await fetchQuizzes();
      
      // Czyścimy aktualnie edytowany quiz
      setCurrentQuiz(null);
      
      return true;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [fetchQuizzes]);

  // Wycofanie publikacji quizu
  const unpublishQuiz = useCallback(async (quizData: QuizEditorVM) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const updateData: QuizUpdateDto = {
        ...mapQuizVMToUpdateDto(quizData),
        status: 'draft'
      };
      
      if (quizData.id) {
        await api.put(`/quizzes/${quizData.id}`, updateData);
      }
      
      await fetchQuizzes();
      setCurrentQuiz(null);
      
      return true;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [fetchQuizzes]);

  // Usuwanie quizu
  const deleteQuiz = useCallback(async (quizId: number) => {
    try {
      setIsLoading(true);
      setError(null);
      
      await api.delete(`/quizzes/${quizId}`);
      
      // Odświeżamy listę quizów
      await fetchQuizzes();
      
      return true;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Wystąpił nieznany błąd'));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [fetchQuizzes]);

  // Czyszczenie aktualnie wybranego quizu
  const clearSelection = useCallback(() => {
    setCurrentQuiz(null);
  }, []);

  // Inicjalizacja - pobieramy poziomy przy pierwszym renderze
  useEffect(() => {
    fetchLevels();
  }, [fetchLevels]);

  const actions = useMemo(() => ({
    fetchQuizzes,
    selectQuizForEdit,
    createNewQuiz,
    saveQuiz,
    publishQuiz,
    unpublishQuiz,
    deleteQuiz,
    clearSelection
  }), [
    fetchQuizzes,
    selectQuizForEdit,
    createNewQuiz,
    saveQuiz,
    publishQuiz,
    unpublishQuiz,
    deleteQuiz,
    clearSelection
  ]);

  return {
    quizzes,
    currentQuiz,
    isLoading,
    error,
    actions
  };
}; 