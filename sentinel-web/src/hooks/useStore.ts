/**
 * Zustand Store
 * 
 * Central state management for Sentinel dashboard.
 */

import { create } from 'zustand';
import { Task, LogEntry } from '@/lib/types/task';

type ActivePanel = 'logs' | 'preview' | 'diffs';

interface AppState {
    // Tasks
    tasks: Task[];
    activeTaskId: string | null;

    // UI State
    sidebarOpen: boolean;
    activePanel: ActivePanel;

    // WebSocket
    connected: boolean;

    // Actions
    addTask: (task: Task) => void;
    updateTask: (id: string, updates: Partial<Task>) => void;
    setActiveTask: (id: string | null) => void;
    addLog: (taskId: string, log: LogEntry) => void;
    toggleSidebar: () => void;
    setActivePanel: (panel: ActivePanel) => void;
    setConnected: (connected: boolean) => void;
    clearTasks: () => void;

    // Operation management
    updateOperationStatus: (taskId: string, operationId: string, status: 'pending' | 'approved' | 'rejected') => void;
    bulkUpdateOperations: (taskId: string, status: 'pending' | 'approved' | 'rejected') => void;
}

export const useStore = create<AppState>((set, get) => ({
    // Initial state
    tasks: [],
    activeTaskId: null,
    sidebarOpen: true,
    activePanel: 'logs',
    connected: false,

    // Task actions
    addTask: (task) => set((state) => ({
        tasks: [task, ...state.tasks],
        activeTaskId: task.id,
    })),

    updateTask: (id, updates) => set((state) => ({
        tasks: state.tasks.map((task) =>
            task.id === id ? { ...task, ...updates } : task
        ),
    })),

    setActiveTask: (id) => set({ activeTaskId: id }),

    addLog: (taskId, log) => set((state) => ({
        tasks: state.tasks.map((task) =>
            task.id === taskId
                ? { ...task, logs: [...task.logs, log] }
                : task
        ),
    })),

    // UI actions
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

    setActivePanel: (panel) => set({ activePanel: panel }),

    setConnected: (connected) => set({ connected }),

    clearTasks: () => set({ tasks: [], activeTaskId: null }),

    // Operation actions
    updateOperationStatus: (taskId, operationId, status) => set((state) => ({
        tasks: state.tasks.map((task) => {
            if (task.id !== taskId || !task.plan) return task;

            return {
                ...task,
                plan: {
                    ...task.plan,
                    operations: task.plan.operations.map((op: any) =>
                        op.id === operationId ? { ...op, status } : op
                    ),
                },
            };
        }),
    })),

    bulkUpdateOperations: async (taskId, status) => {
        // Optimistic update
        set((state) => ({
            tasks: state.tasks.map((task) => {
                if (task.id !== taskId || !task.plan) return task;

                return {
                    ...task,
                    plan: {
                        ...task.plan,
                        operations: task.plan.operations.map((op: any) =>
                            op.status === 'pending' ? { ...op, status } : op
                        ),
                    },
                };
            }),
        }));

        // API Call
        if (status === 'approved') {
            try {
                const { api } = require('@/lib/api/client');
                await api.approvePlan(taskId);
            } catch (error) {
                console.error('Failed to approve plan:', error);
                // Revert or show error (omitted for brevity)
            }
        }
    },
}));

// Selectors
export const useActiveTask = () => {
    const tasks = useStore((state) => state.tasks);
    const activeTaskId = useStore((state) => state.activeTaskId);
    return tasks.find((task) => task.id === activeTaskId);
};

export const useTaskById = (id: string) => {
    const tasks = useStore((state) => state.tasks);
    return tasks.find((task) => task.id === id);
};
