import { getAccessToken, getApiUrl } from './access';

/**
 * API Client
 * 
 * HTTP client for Sentinel API endpoints.
 */

class APIClient {
    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${getApiUrl()}${endpoint}`;

        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${getAccessToken()}`,
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            const detail = typeof error.detail === 'string' ? error.detail : `HTTP ${response.status}`;
            const retryAfter = response.headers.get('Retry-After');
            if (response.status === 429 && retryAfter && /^\d+$/.test(retryAfter)) {
                throw new Error(`${detail}. Try again in ${retryAfter}s.`);
            }
            throw new Error(detail);
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
        return this.request<{ task_id: string }>('/plan', {
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
    async previewPlan(taskId: string) {
        return this.request('/preview', {
            method: 'POST',
            body: JSON.stringify({ task_id: taskId }),
        });
    }

    // Execute task
    async executeTask(taskId: string, approvedActionIndices: number[]) {
        return this.request('/execute', {
            method: 'POST',
            body: JSON.stringify({
                task_id: taskId,
                approved_action_indices: approvedActionIndices,
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

    async history() {
        return this.request<{ task_id: string; state: string; created_at: string }[]>('/history');
    }

    // Undo task
    async undoTask(taskId: string) {
        return this.request<{ message: string }>('/undo', {
            method: 'POST',
            body: JSON.stringify({ task_id: taskId }),
        });
    }

    // Health check
    async health() {
        return this.request('/health');
    }
}

export const api = new APIClient();
