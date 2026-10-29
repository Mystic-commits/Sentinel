/**
 * API Client
 *
 * HTTP client for Sentinel API endpoints.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const response = await fetch(url, {
      cache: "no-store",
      signal: AbortSignal.timeout(15000),
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      const message = Array.isArray(error.detail)
        ? error.detail.map((item: { msg: string }) => item.msg).join(". ")
        : error.detail;
      throw new Error(message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async createPlan(
    userPrompt: string,
    path: string,
    strategy: "local_ai" | "file_types" = "local_ai",
  ) {
    return this.request("/plan", {
      method: "POST",
      body: JSON.stringify({strategy, user_prompt: userPrompt, path}),
    });
  }

  // Execute task
  async executeTask(taskId: string, approvedActions: number[]) {
    return this.request("/execute", {
      method: "POST",
      body: JSON.stringify({
        task_id: taskId,
        skip_safety: false,
        approved_actions: approvedActions,
      }),
    });
  }

  // Get all tasks
  async getTasks(offset = 0, limit = 100) {
    return this.request(`/tasks?offset=${offset}&limit=${limit}`);
  }

  // Get task by ID
  async getTask(id: string) {
    return this.request(`/tasks/${id}`);
  }

  // Health check
  async health() {
    return this.request("/health");
  }
}

export const api = new APIClient(API_URL);
