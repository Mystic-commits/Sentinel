/**
 * WebSocket Hook
 * 
 * Manages WebSocket connection for real-time task updates with auto-reconnection.
 */

'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useStore } from './useStore';
import { LogEntry, TaskState, TaskResult } from '@/lib/types/task';

import { api, APIError } from '@/lib/api/client';
import { getAccessToken, getEventsUrl } from '@/lib/api/access';

const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 5;

interface WebSocketMessage {
    event_type: string;
    task_id?: string;
    timestamp: string;
    message?: string;
    data: Record<string, any>;
}

export function useWebSocket() {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectAttemptsRef = useRef(0);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
    const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

    const { updateTask, addLog, setConnected } = useStore();

    const createLog = (message: string, level: LogEntry['level'], timestamp: string): LogEntry => ({
        id: crypto.randomUUID(),
        message,
        level,
        timestamp: timestamp || new Date().toISOString(),
    });

    const handleMessage = useCallback((message: WebSocketMessage) => {
        const { event_type, task_id, message: msg, timestamp, data } = message;



        switch (event_type) {
            case 'CONNECTION_ACK':
                console.log('✅ Connection acknowledged:', data);
                break;

            case 'HEARTBEAT':
                // Silent heartbeat - no action needed
                break;

            case 'TASK_STARTED':
                if (task_id) {
                    updateTask(task_id, { state: 'scanning' as TaskState });
                    addLog(task_id, createLog(msg || 'Task started', 'info', timestamp));
                }
                break;

            case 'SCAN_PROGRESS':
                if (task_id) {
                    const progress = data.progress || 0;
                    const currentFile = data.current_file || '';
                    addLog(task_id, createLog(
                        msg || `Scanning: ${currentFile}`,
                        'info',
                        timestamp
                    ));
                }
                break;

            case 'PLAN_READY':
                if (task_id) {
                    if (useStore.getState().tasks.find(task => task.id === task_id)?.plan) break;
                    // Map backend 'actions' to frontend 'operations'
                    const backendPlan = data.plan;
                    const rawOps = backendPlan.actions || backendPlan.operations || [];

                    // CRITICAL: Initialize each operation with 'pending' status and unique id
                    // Backend PlanAction has no status/id fields — without this, all buttons are disabled
                    const operations = rawOps.map((op: any, index: number) => ({
                        ...op,
                        id: op.id || `op-${index}`,
                        status: op.status || 'pending',
                        source: op.source || op.source_path || '',
                        destination: op.destination || op.destination_path || '',
                    }));

                    const mappedPlan = {
                        ...backendPlan,
                        operations,
                        planningSource: data.summary?.planning_source,
                    };

                    updateTask(task_id, {
                        state: 'review' as TaskState,
                        plan: mappedPlan,
                    });
                    addLog(task_id, createLog(
                        msg || `Plan ready: ${operations.length} operations`,
                        'success',
                        timestamp
                    ));
                }
                break;

            case 'WAITING_FOR_APPROVAL':
                if (task_id) {
                    updateTask(task_id, { state: 'review' as TaskState });
                    addLog(task_id, createLog(
                        msg || 'Waiting for your approval',
                        'info',
                        timestamp
                    ));
                }
                break;

            case 'EXECUTION_PROGRESS':
                if (task_id) {
                    const progress = data.progress || 0;
                    updateTask(task_id, {
                        state: 'executing' as TaskState,
                        progress,
                    });
                    addLog(task_id, createLog(
                        msg || `Executing: ${progress}%`,
                        'info',
                        timestamp
                    ));
                }
                break;

            case 'TASK_COMPLETED':
                if (task_id) {
                    updateTask(task_id, {
                        state: 'completed' as TaskState,
                        progress: 100,
                        result: data.result,
                    });
                    addLog(task_id, createLog(
                        msg || 'Task completed successfully',
                        'success',
                        timestamp
                    ));
                }
                break;

            case 'TASK_FAILED':
                if (task_id) {
                    updateTask(task_id, { state: 'failed' as TaskState });
                    addLog(task_id, createLog(
                        msg || `Task failed: ${data.error}`,
                        'error',
                        timestamp
                    ));
                }
                break;

            // Legacy events (kept for compatibility)
            case 'SCANNING':
                if (task_id) {
                    updateTask(task_id, { state: 'scanning' as TaskState });
                    addLog(task_id, createLog(msg || 'Scanning directory...', 'info', timestamp));
                }
                break;

            case 'SCAN_COMPLETE':
                if (task_id) {
                    addLog(task_id, createLog(
                        msg || `Scan complete. Found ${data.file_count || 0} files.`,
                        'success',
                        timestamp
                    ));
                }
                break;

            case 'PLANNING':
                if (task_id) {
                    updateTask(task_id, { state: 'planning' as TaskState });
                    addLog(task_id, createLog(msg || 'AI creating organization plan...', 'info', timestamp));
                }
                break;

            case 'SAFETY_CHECK':
                if (task_id) {
                    addLog(task_id, createLog(msg || 'Running safety checks...', 'info', timestamp));
                }
                break;

            case 'EXECUTING':
                if (task_id) {
                    updateTask(task_id, { state: 'executing' as TaskState });
                    addLog(task_id, createLog(msg || 'Executing plan...', 'info', timestamp));
                }
                break;

            case 'PROGRESS':
                if (task_id) {
                    const progress = data.progress || 0;
                    updateTask(task_id, { progress });
                    addLog(task_id, createLog(msg || `Progress: ${progress}%`, 'info', timestamp));
                }
                break;

            case 'COMPLETE':
                if (task_id) {
                    updateTask(task_id, {
                        state: 'completed' as TaskState,
                        progress: 100,
                        result: data as unknown as TaskResult,
                    });
                    addLog(task_id, createLog(msg || 'Task completed successfully', 'success', timestamp));
                }
                break;

            case 'FAILED':
            case 'ERROR':
                if (task_id) {
                    updateTask(task_id, { state: 'failed' as TaskState });
                    addLog(task_id, createLog(msg || 'Task failed', 'error', timestamp));
                }
                break;

            default:
                console.warn('Unknown event type:', event_type);
        }
    }, [updateTask, addLog]);

    const connect = useCallback(function connect() {
        // Don't reconnect if already connected
        if (wsRef.current && wsRef.current.readyState <= WebSocket.OPEN) {
            return;
        }

        setConnectionState('connecting');
        console.log('🔌 Connecting to WebSocket...');

        const ws = new WebSocket(getEventsUrl(), ['sentinel.events.v1', `auth.${getAccessToken()}`]);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('✅ WebSocket connected');
            setConnectionState('connected');
            setConnected(true);
            reconnectAttemptsRef.current = 0; // Reset attempts on successful connection
        };

        ws.onclose = (event) => {
            console.log(`🔌 WebSocket disconnected (code: ${event.code}, reason: ${event.reason})`);
            setConnectionState('disconnected');
            setConnected(false);

            // Attempt reconnection
            if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttemptsRef.current++;
                console.log(`🔄 Reconnecting in ${RECONNECT_DELAY}ms... (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);

                reconnectTimeoutRef.current = setTimeout(() => {
                    connect();
                }, RECONNECT_DELAY);
            } else {
                console.error('❌ Max reconnection attempts reached. Please reload the page.');
            }
        };

        ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
            setConnected(false);
        };

        ws.onmessage = (event) => {
            try {
                const message: WebSocketMessage = JSON.parse(event.data);
                handleMessage(message);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };
    }, [setConnected, handleMessage]);

    useEffect(() => {
        connect();

        return () => {
            // Cleanup on unmount
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            const socket = wsRef.current;
            wsRef.current = null;
            if (socket) {
                socket.onclose = null;
                socket.onmessage = null;
                socket.onopen = null;
                socket.onerror = null;
                socket.close();
            }
            setConnected(false);
        };
    }, [connect, setConnected]);

    // A fast plan can finish before its HTTP response arrives. Recover missed terminal
    // events from the API without resetting approvals already made in a review.
    useEffect(() => {
        let active = true;
        let timer: ReturnType<typeof setTimeout>;
        async function reconcile() {
            for (const task of useStore.getState().tasks) {
                if (!active) return;
                if (task.state !== 'planning' && task.state !== 'executing') continue;
                try {
                    const detail = await api.getTask(task.id);
                    if (!active || useStore.getState().tasks.find(item => item.id === task.id)?.state !== task.state) continue;
                    if (detail.state === 'review' && detail.plan) {
                        handleMessage({
                            event_type: 'PLAN_READY', task_id: task.id, timestamp: new Date().toISOString(),
                            data: { plan: detail.plan, summary: { planning_source: detail.planning_source } },
                        });
                    } else if (detail.state === 'failed' || detail.state === 'completed') {
                        handleMessage({
                            event_type: detail.state === 'failed' ? 'ERROR' : 'COMPLETE',
                            task_id: task.id, timestamp: new Date().toISOString(), data: {},
                            message: detail.state === 'failed' ? (task.state === 'planning' ? detail.summary : '') || 'Task failed. Check execution history.' : 'Task completed',
                        });
                    }
                } catch (error) {
                    if (active && error instanceof APIError && error.status === 404) {
                        handleMessage({
                            event_type: 'ERROR', task_id: task.id, timestamp: new Date().toISOString(), data: {},
                            message: 'The backend no longer has this task. Check execution history before scanning again.',
                        });
                    }
                }
            }
            if (active) timer = setTimeout(reconcile, RECONNECT_DELAY);
        }
        timer = setTimeout(reconcile, RECONNECT_DELAY);
        return () => { active = false; clearTimeout(timer); };
    }, [handleMessage]);

    const send = useCallback((data: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        } else {
            console.warn('⚠️ WebSocket not connected, cannot send:', data);
        }
    }, []);

    return {
        send,
        connectionState,
        reconnect: connect,
    };
}
