/**
 * API Client
 * 
 * HTTP client for Sentinel API endpoints.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class APIClient {
    private baseURL: string;

    constructor(baseURL: string) {
        this.baseURL = baseURL;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;

        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Scan directory
    async scan(path: string, recursive: boolean = true) {
        return this.request('/scan', {
            method: 'POST',
            body: JSON.stringify({ path, recursive }),
        });
    }

    // Create plan
    async createPlan(scanId: string | null, mode: string, userPrompt?: string, path?: string) {
        return this.request('/plan', {
            method: 'POST',
            body: JSON.stringify({
                scan_id: scanId,
                mode,
                user_prompt: userPrompt,
                path: path,
            }),
        });
    }

    // Preview plan
    async previewPlan(planId: string) {
        return this.request('/preview', {
            method: 'POST',
            body: JSON.stringify({ plan_id: planId }),
        });
    }

    // Approve plan
    async approvePlan(taskId: string) {
        return this.request(`/plan/${taskId}/approve-all`, {
            method: 'POST',
        });
    }

    // Execute task
    async executeTask(taskId: string) {
        return this.request('/execute', {
            method: 'POST',
            body: JSON.stringify({
                task_id: taskId,
                skip_safety: false, // Always false
            }),
        });
    }

    // Get all tasks
    async getTasks() {
        return this.request('/tasks');
    }

    // Get task by ID
    async getTask(id: string) {
        return this.request(`/tasks/${id}`);
    }

    // Undo task
    async undoTask(taskId: string) {
        return this.request('/undo', {
            method: 'POST',
            body: JSON.stringify({ task_id: taskId }),
        });
    }

    // Health check
    async health() {
        return this.request('/health');
    }
}

export const api = new APIClient(API_URL);
