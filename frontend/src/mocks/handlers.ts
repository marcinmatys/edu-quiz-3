import { http, HttpResponse } from "msw";

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

export const handlers = [
  // Handle token endpoint
  http.post("/api/v1/auth/token", async ({ request }) => {
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
  http.get("/api/v1/users/me", ({ request }) => {
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
]; 