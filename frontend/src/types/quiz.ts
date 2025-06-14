// Typy DTO - zgodne z API
export interface QuizListItemDto {
  id: number;
  title: string;
  status: 'published' | 'draft';
  level_id: number;
  question_count: number;
  updated_at: string;
  creator_id: number;
}

export interface AnswerDto {
  id?: number;
  text: string;
  is_correct: boolean;
}

export interface QuestionDto {
  id?: number;
  text: string;
  answers: AnswerDto[];
}

export interface QuizUpdateDto {
  title?: string;
  level_id?: number;
  status?: 'published' | 'draft';
  questions?: QuestionDto[];
}

export interface CreateQuizRequestDto {
  topic: string;
  question_count: number;
  level_id: number;
  title: string;
}

export interface LevelDto {
  id: number;
  code: string;
  description: string;
  level: number;
}

// Typy ViewModel - na potrzeby widoku
export interface QuizListItemVM extends Omit<QuizListItemDto, 'level_id'> {
  level: string; // np. "Klasa IV" zamiast ID
}

// Typ dla stanu edytora quizów
export interface AnswerVM {
  id?: number;
  uiId: string; // Unikalne ID na potrzeby UI (np. dla kluczy w listach Reacta)
  text: string;
  is_correct: boolean;
}

export interface QuestionVM {
  id?: number;
  uiId: string;
  text: string;
  answers: AnswerVM[];
}

export interface QuizEditorVM {
  id?: number;
  title: string;
  level_id: number;
  questions: QuestionVM[];
}

// Typ dla filtrów listy quizów
export interface QuizFilters {
  status?: 'published' | 'draft' | 'all';
} 