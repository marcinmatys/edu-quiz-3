// Typy DTO - zgodne z API
export interface LastResultDto {
  score: number;
  max_score: number;
}

export interface QuizListItemDto {
  id: number;
  title: string;
  status: 'published' | 'draft';
  level_id: number;
  question_count: number;
  updated_at: string;
  creator_id: number;
  last_result?: LastResultDto | null;
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
  status: 'draft' | 'published';
  questions: QuestionVM[];
}

// Typ dla filtrów listy quizów
export interface QuizFilters {
  status?: 'published' | 'draft' | 'all';
}

// Model widoku dla komponentu QuizCard w panelu ucznia
export interface QuizCardViewModel {
  id: number;
  title: string;
  levelDescription: string;     // np. "Klasa IV"
  questionCountText: string;    // np. "Liczba pytań: 10"
  lastResultText: string | null;  // np. "Ostatni wynik: 8/10"
  startQuizPath: string;        // np. "/student/quiz/5"
}

// Typ dla parametrów sortowania listy quizów ucznia
export interface SortParams {
  sortBy: string;
  order: 'asc' | 'desc';
}

// --- DTOs for Quiz Taking ---

// Odpowiedź serwera dla GET /quizzes/{quiz_id} (dla studenta)
export interface AnswerReadStudentDto {
  id: number;
  text: string;
}

export interface QuestionReadStudentDto {
  id: number;
  text: string;
  answers: AnswerReadStudentDto[];
}

export interface QuizReadDetailStudentDto {
  id: number;
  title: string;
  level_id: number;
  status: string;
  creator_id: number;
  updated_at: string;
  questions: QuestionReadStudentDto[];
}

// Ciało żądania dla POST /quizzes/{quiz_id}/check-answer
export interface AnswerCheckRequestDto {
  question_id: number;
  answer_id: number;
}

// Odpowiedź serwera dla POST /quizzes/{quiz_id}/check-answer
export interface AnswerCheckResponseDto {
  is_correct: boolean;
  correct_answer_id: number;
  explanation: string;
}

// Ciało żądania dla POST /quizzes/{quiz_id}/results
export interface ResultCreateDto {
  score: number;
  max_score: number;
}

// --- ViewModels for Quiz Taking ---

// Typ określający status wizualny odpowiedzi w UI
export type AnswerStatus = 'default' | 'selected' | 'correct' | 'incorrect';

// Model widoku dla pojedynczej odpowiedzi
export interface AnswerStateViewModel {
  id: number;
  text: string;
  status: AnswerStatus;
} 