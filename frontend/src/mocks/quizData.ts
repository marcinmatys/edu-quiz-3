import type { QuizListItemDto, LevelDto } from '../types/quiz';

export const mockLevels: LevelDto[] = [
  { id: 1, code: 'Klasa IV', description: 'Szkoła podstawowa, klasa 4', level: 4 },
  { id: 2, code: 'Klasa V', description: 'Szkoła podstawowa, klasa 5', level: 5 },
  { id: 3, code: 'Klasa VI', description: 'Szkoła podstawowa, klasa 6', level: 6 },
  { id: 4, code: 'Klasa VII', description: 'Szkoła podstawowa, klasa 7', level: 7 },
  { id: 5, code: 'Klasa VIII', description: 'Szkoła podstawowa, klasa 8', level: 8 },
];

export const mockQuizzes: QuizListItemDto[] = [
  {
    id: 1,
    title: 'Podstawy fotosyntesy',
    status: 'published',
    level_id: 4,
    question_count: 10,
    updated_at: '2023-11-15T10:30:00Z',
    creator_id: 1
  },
  {
    id: 2,
    title: 'Układ słoneczny',
    status: 'published',
    level_id: 5,
    question_count: 8,
    updated_at: '2023-11-10T14:20:00Z',
    creator_id: 1
  },
  {
    id: 3,
    title: 'Historia Polski - zaborów',
    status: 'draft',
    level_id: 7,
    question_count: 15,
    updated_at: '2023-11-18T09:15:00Z',
    creator_id: 1
  },
  {
    id: 4,
    title: 'Matematyka - ułamki',
    status: 'draft',
    level_id: 4,
    question_count: 12,
    updated_at: '2023-11-17T16:45:00Z',
    creator_id: 1
  },
  {
    id: 5,
    title: 'Angielski - czasy przeszłe',
    status: 'published',
    level_id: 6,
    question_count: 20,
    updated_at: '2023-11-05T11:10:00Z',
    creator_id: 1
  },
];

export const mockQuizDetail = {
  id: 3,
  title: 'Historia Polski - zaborów',
  status: 'draft',
  level_id: 7,
  creator_id: 1,
  updated_at: '2023-11-18T09:15:00Z',
  questions: [
    {
      id: 1,
      text: 'Kiedy nastąpił pierwszy rozbiór Polski?',
      answers: [
        { id: 1, text: '1772', is_correct: true },
        { id: 2, text: '1793', is_correct: false },
        { id: 3, text: '1795', is_correct: false },
        { id: 4, text: '1791', is_correct: false },
      ],
    },
    {
      id: 2,
      text: 'Które państwa uczestniczyły w trzecim rozbiorze Polski?',
      answers: [
        { id: 5, text: 'Rosja, Prusy i Austria', is_correct: true },
        { id: 6, text: 'Rosja i Prusy', is_correct: false },
        { id: 7, text: 'Rosja i Austria', is_correct: false },
        { id: 8, text: 'Prusy i Austria', is_correct: false },
      ],
    },
    {
      id: 3,
      text: 'W którym roku uchwalono Konstytucję 3 Maja?',
      answers: [
        { id: 9, text: '1791', is_correct: true },
        { id: 10, text: '1793', is_correct: false },
        { id: 11, text: '1795', is_correct: false },
        { id: 12, text: '1772', is_correct: false },
      ],
    },
  ],
}; 