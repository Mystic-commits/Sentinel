import type { TaskState } from '@/lib/types/task';
import { getAccessToken, getApiUrl } from './access';

/**
 * API Client
 * 
 * HTTP client for Sentinel API endpoints.
 */

export class APIError extends Error {
    constructor(readonly status: number, message: string) { super(message); }
}

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
            const detail = typeof error.detail === 'string' ? error.detail : error.detail?.[0]?.msg || `HTTP ${response.status}`;
            const retryAfter = response.headers.get('Retry-After');
            if (response.status === 429 && retryAfter && /^\d+$/.test(retryAfter)) {
                throw new Error(`${detail}. Try again in ${retryAfter}s.`);
            }
            throw new APIError(response.status, detail);
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
    async createPlan(path: string, useAi: boolean, userPrompt?: string) {
        return this.request<{ task_id: string }>('/plan', {
            method: 'POST',
            body: JSON.stringify({ path, use_ai: useAi, user_prompt: userPrompt }),
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
        return this.request<{ state: TaskState; plan: Record<string, unknown> | null; planning_source: string | null; summary: string }>(`/tasks/${encodeURIComponent(id)}`);
    }

    async history() {
        return this.request<{
            task_id: string;
            state: string;
            created_at: string;
            operation_count: number;
            applied_count: number;
            restored_count: number;
            uncertain_count: number;
        }[]>('/history');
    }

    async receiptDetails(taskId: string) {
        return this.request<{
            index: number;
            source: string;
            destination: string;
            apply_state: 'pending' | 'started' | 'done';
            undo_state: 'pending' | 'started' | 'done';
        }[]>(`/history/${encodeURIComponent(taskId)}`);
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
