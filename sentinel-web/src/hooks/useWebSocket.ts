/**
 * WebSocket Hook
 * 
 * Manages WebSocket connection for real-time task updates with auto-reconnection.
 */

'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useStore } from './useStore';
import { LogEntry, TaskState, TaskResult } from '@/lib/types/task';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/events';
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
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
    const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

    const { updateTask, addLog, setConnected } = useStore();

    const connect = useCallback(() => {
        // Don't reconnect if already connected
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        setConnectionState('connecting');
        console.log('🔌 Connecting to WebSocket...');

        const ws = new WebSocket(WS_URL);
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
    }, [setConnected]);

    const handleMessage = useCallback((message: WebSocketMessage) => {
        const { event_type, task_id, message: msg, timestamp, data } = message;

        console.log(`📨 WebSocket event: ${event_type}`, { task_id, data });

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

    const createLog = (message: string, level: LogEntry['level'], timestamp: string): LogEntry => ({
        id: crypto.randomUUID(),
        message,
        level,
        timestamp: timestamp || new Date().toISOString(),
    });

    useEffect(() => {
        connect();

        return () => {
            // Cleanup on unmount
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.close();
            }
        };
    }, [connect]);

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
