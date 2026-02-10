/**
 * Task Type Definitions
 */

export type TaskMode =
    | 'file_organization'
    | 'pc_cleanup'
    | 'media_sort'
    | 'safe_delete'
    | 'ask_ai';

export type TaskState =
    | 'idle'
    | 'scanning'
    | 'planning'
    | 'review'
    | 'executing'
    | 'completed'
    | 'failed';

export interface LogEntry {
    id: string;
    message: string;
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'success';
}

export interface FileOperation {
    type: 'move' | 'delete' | 'create';
    source: string;
    destination?: string;
    reason?: string;
}

export interface Plan {
    id: string;
    task_id: string;
    operations: FileOperation[];
    total_files: number;
    estimated_time?: string;
    created_at: string;
}

export interface TaskResult {
    success: boolean;
    files_processed: number;
    errors: string[];
    completed_at: string;
}

export interface Task {
    id: string;
    description: string;
    mode: TaskMode;
    state: TaskState;
    path?: string;
    created_at: string;
    updated_at: string;
    logs: LogEntry[];
    plan?: Plan;
    result?: TaskResult;
    progress?: number;
}

export const TASK_MODES: Array<{ id: TaskMode; label: string; description: string }> = [
    {
        id: 'file_organization',
        label: 'Organize',
        description: 'Organize files by type, date, or custom rules'
    },
    {
        id: 'pc_cleanup',
        label: 'Cleanup',
        description: 'Remove duplicates, old files, and clutter'
    },
    {
        id: 'media_sort',
        label: 'Media',
        description: 'Organize photos and videos by date/event'
    },
    {
        id: 'safe_delete',
        label: 'Delete',
        description: 'Safely move unwanted files to trash'
    },
    {
        id: 'ask_ai',
        label: 'Custom',
        description: 'Custom AI-powered file organization'
    },
];

export const STATE_CONFIG: Record<TaskState, { label: string; color: string }> = {
    idle: { label: 'Idle', color: 'text-[#666]' },
    scanning: { label: 'Scanning', color: 'text-[#999]' },
    planning: { label: 'Planning', color: 'text-[#999]' },
    review: { label: 'Review', color: 'text-[#ededed]' },
    executing: { label: 'Running', color: 'text-[#ededed]' },
    completed: { label: 'Done', color: 'text-emerald-400' },
    failed: { label: 'Failed', color: 'text-red-400' },
};
