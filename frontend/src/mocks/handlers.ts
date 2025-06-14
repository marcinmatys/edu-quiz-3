import { http, HttpResponse } from "msw";
import { mockLevels, mockQuizzes, mockQuizDetail } from "./quizData";
import { v4 as uuidv4 } from "uuid";
import type { QuizListItemDto } from "../types/quiz";

// Define API prefix constant
const API_V1_PREFIX = "/api/v1";

// Mock user data
const users = [
  {
    id: 1,
    username: "admin",
    password: "admin123",
    role: "admin",
    is_active: true,
    created_at: "2023-01-01T00:00:00Z",
  },
  {
    id: 2,
    username: "student",
    password: "student123",
    role: "student",
    is_active: true,
    created_at: "2023-01-01T00:00:00Z",
  },
];

// Store active tokens
const activeTokens = new Map<string, number>();

// Deep clone the mock quizzes to avoid modifying the original data
let quizzes = JSON.parse(JSON.stringify(mockQuizzes)) as QuizListItemDto[];
let quizDetail = JSON.parse(JSON.stringify(mockQuizDetail));

// Helper type for quiz status
type QuizStatus = "draft" | "published";

export const handlers = [
  // Handle token endpoint
  http.post(`${API_V1_PREFIX}/auth/token`, async ({ request }) => {
    const formData = await request.formData();
    const username = formData.get("username") as string | null;
    const password = formData.get("password") as string | null;

    // Find user
    const user = users.find(
      (u) => u.username === username && u.password === password
    );

    if (!user) {
      return new HttpResponse(null, {
        status: 401,
        statusText: "Unauthorized",
      });
    }

    // Generate token (in a real app this would be a JWT)
    const token = `mock-token-${user.id}-${Date.now()}`;
    
    // Store token with user ID
    activeTokens.set(token, user.id);

    return HttpResponse.json({
      access_token: token,
      token_type: "bearer",
    });
  }),

  // Handle get user endpoint
  http.get(`${API_V1_PREFIX}/users/me`, ({ request }) => {
    const authHeader = request.headers.get("Authorization");
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return new HttpResponse(null, {
        status: 401,
        statusText: "Unauthorized",
      });
    }

    const token = authHeader.split(" ")[1];
    const userId = activeTokens.get(token);

    if (!userId) {
      return new HttpResponse(null, {
        status: 401,
        statusText: "Unauthorized",
      });
    }

    // Find user by ID
    const user = users.find((u) => u.id === userId);
    
    if (!user) {
      return new HttpResponse(null, {
        status: 404,
        statusText: "Not Found",
      });
    }

    // Return user data without password
    const { password, ...userData } = user;
    return HttpResponse.json(userData);
  }),

  // Get all quizzes
  http.get(`${API_V1_PREFIX}/quizzes`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get("status");
    
    let filteredQuizzes = quizzes;
    
    if (status && status !== 'all') {
      filteredQuizzes = quizzes.filter((quiz: QuizListItemDto) => quiz.status === status);
    }
    
    return HttpResponse.json(filteredQuizzes);
  }),

  // Get a single quiz
  http.get(`${API_V1_PREFIX}/quizzes/:id`, ({ params }) => {
    const id = Number(params.id);
    
    if (id === quizDetail.id) {
      return HttpResponse.json(quizDetail);
    }
    
    const quiz = quizzes.find((q: QuizListItemDto) => q.id === id);
    
    if (!quiz) {
      return new HttpResponse(null, {
        status: 404,
        statusText: "Not Found",
      });
    }
    
    // For simplicity, we'll return the mock quiz detail with updated ID and title
    const customQuizDetail = {
      ...JSON.parse(JSON.stringify(quizDetail)),
      id: quiz.id,
      title: quiz.title,
      status: quiz.status,
      level_id: quiz.level_id,
    };
    
    return HttpResponse.json(customQuizDetail);
  }),

  // Create a new quiz
  http.post(`${API_V1_PREFIX}/quizzes`, async ({ request }) => {
    const quizData = await request.json() as any;
    
    // Ensure status is a valid QuizStatus
    const status: QuizStatus = quizData.status === "published" ? "published" : "draft";
    
    const newQuiz: QuizListItemDto = {
      id: Math.max(...quizzes.map(q => q.id)) + 1,
      title: quizData.title,
      status: status,
      level_id: quizData.level_id,
      question_count: quizData.questions ? quizData.questions.length : 0,
      updated_at: new Date().toISOString(),
      creator_id: 1,
    };
    
    quizzes = [...quizzes, newQuiz];
    
    return HttpResponse.json(newQuiz, { status: 201 });
  }),

  // Update a quiz
  http.put(`${API_V1_PREFIX}/quizzes/:id`, async ({ request, params }) => {
    const id = Number(params.id);
    const quizData = await request.json() as any;
    
    const quizIndex = quizzes.findIndex(q => q.id === id);
    
    if (quizIndex === -1) {
      return new HttpResponse(null, {
        status: 404,
        statusText: "Not Found",
      });
    }
    
    // Ensure status is a valid QuizStatus
    const status: QuizStatus = quizData.status === "published" ? "published" : "draft";
    
    const updatedQuiz: QuizListItemDto = {
      ...quizzes[quizIndex],
      title: quizData.title || quizzes[quizIndex].title,
      status: status,
      level_id: quizData.level_id || quizzes[quizIndex].level_id,
      question_count: quizData.questions ? quizData.questions.length : quizzes[quizIndex].question_count,
      updated_at: new Date().toISOString(),
    };
    
    quizzes = [
      ...quizzes.slice(0, quizIndex),
      updatedQuiz,
      ...quizzes.slice(quizIndex + 1)
    ];
    
    if (id === quizDetail.id) {
      quizDetail = {
        ...quizDetail,
        title: updatedQuiz.title,
        status: updatedQuiz.status,
        level_id: updatedQuiz.level_id,
        updated_at: updatedQuiz.updated_at,
        questions: quizData.questions || quizDetail.questions,
      };
    }
    
    return HttpResponse.json(updatedQuiz);
  }),

  // Delete a quiz
  http.delete(`${API_V1_PREFIX}/quizzes/:id`, ({ params }) => {
    const id = Number(params.id);
    const quizIndex = quizzes.findIndex(q => q.id === id);
    
    if (quizIndex === -1) {
      return new HttpResponse(null, {
        status: 404,
        statusText: "Not Found",
      });
    }
    
    quizzes = [
      ...quizzes.slice(0, quizIndex),
      ...quizzes.slice(quizIndex + 1)
    ];
    
    return new HttpResponse(null, { status: 204 });
  }),

  // Generate a quiz with AI
  http.post(`${API_V1_PREFIX}/quizzes/generate`, async ({ request }) => {
    const data = await request.json() as any;
    
    // Simulate AI generation delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const newQuiz = {
      id: Math.max(...quizzes.map(q => q.id)) + 1,
      title: data.title,
      status: "draft" as QuizStatus,
      level_id: data.level_id,
      creator_id: 1,
      updated_at: new Date().toISOString(),
      questions: Array.from({ length: data.question_count }, (_, i) => ({
        id: i + 1,
        text: `Pytanie ${i + 1} na temat: ${data.topic}`,
        answers: [
          { id: i * 4 + 1, text: `Odpowiedź 1 do pytania ${i + 1}`, is_correct: true },
          { id: i * 4 + 2, text: `Odpowiedź 2 do pytania ${i + 1}`, is_correct: false },
          { id: i * 4 + 3, text: `Odpowiedź 3 do pytania ${i + 1}`, is_correct: false },
          { id: i * 4 + 4, text: `Odpowiedź 4 do pytania ${i + 1}`, is_correct: false },
        ],
      })),
    };
    
    // Add to the quizzes list
    quizzes = [
      ...quizzes,
      {
        id: newQuiz.id,
        title: newQuiz.title,
        status: newQuiz.status,
        level_id: newQuiz.level_id,
        question_count: newQuiz.questions.length,
        updated_at: newQuiz.updated_at,
        creator_id: newQuiz.creator_id,
      } as QuizListItemDto
    ];
    
    return HttpResponse.json(newQuiz);
  }),

  // Get all levels
  http.get(`${API_V1_PREFIX}/levels`, () => {
    return HttpResponse.json(mockLevels);
  }),
];