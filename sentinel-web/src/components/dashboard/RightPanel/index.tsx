'use client';

import { useStore, useActiveTask } from '@/hooks/useStore';
import { LogEntry } from '@/lib/types/task';
import { useEffect, useRef } from 'react';

type Tab = 'logs' | 'preview' | 'diffs';

const TABS: Tab[] = ['logs', 'preview', 'diffs'];

export default function RightPanel() {
    const { activePanel, setActivePanel } = useStore();
    const activeTask = useActiveTask();

    return (
        <div className="w-80 flex flex-col h-screen bg-surface-1 border-l border-edge">
            {/* Tabs */}
            <div className="flex h-12 border-b border-edge">
                {TABS.map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActivePanel(tab)}
                        className={`
                            flex-1 text-[13px] font-medium capitalize transition-colors relative
                            ${activePanel === tab
                                ? 'text-txt-primary'
                                : 'text-txt-faint hover:text-txt-secondary'
                            }
                        `}
                    >
                        {tab === 'diffs' ? 'Operations' : tab}
                        {activePanel === tab && (
                            <div className="absolute bottom-0 inset-x-3 h-[2px] bg-txt-primary rounded-full" />
                        )}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden">
                {activePanel === 'logs' && <LogsPanel task={activeTask} />}
                {activePanel === 'preview' && <PreviewPanel task={activeTask} />}
                {activePanel === 'diffs' && <DiffsPanel task={activeTask} />}
            </div>
        </div>
    );
}

function LogsPanel({ task }: { task: any }) {
    const logsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [task?.logs]);

    if (!task) {
        return <EmptyState message="No active task" />;
    }

    return (
        <div className="h-full overflow-y-auto p-4 space-y-0.5 font-mono text-[13px]">
            {task.logs.length === 0 ? (
                <EmptyState message="Waiting for logs..." />
            ) : (
                <>
                    {task.logs.map((log: LogEntry) => (
                        <LogLine key={log.id} log={log} />
                    ))}
                    <div ref={logsEndRef} />
                </>
            )}
        </div>
    );
}

function LogLine({ log }: { log: LogEntry }) {
    const colors = {
        info: 'text-txt-secondary',
        success: 'text-emerald-400',
        warning: 'text-amber-400',
        error: 'text-red-400',
    };

    return (
        <div className={`${colors[log.level]} py-1 leading-relaxed flex gap-2`}>
            <span className="text-txt-faint shrink-0">
                {new Date(log.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                })}
            </span>
            <span>{log.message}</span>
        </div>
    );
}

function PreviewPanel({ task }: { task: any }) {
    if (!task?.plan) {
        return <EmptyState message="No plan yet" />;
    }

    const ops = task.plan.operations || [];

    return (
        <div className="h-full overflow-y-auto p-4 space-y-2">
            <p className="text-[12px] text-txt-muted font-medium mb-3">
                {ops.length} operations planned
            </p>

            {ops.map((op: any, i: number) => (
                <div key={i} className="py-2.5 border-b border-edge/50">
                    <span className="text-[12px] font-semibold text-txt-secondary uppercase tracking-wide">
                        {op.type}
                    </span>
                    <p className="font-mono text-[12px] text-txt-muted break-all mt-1 leading-relaxed">
                        {op.source || op.source_path}
                    </p>
                    {(op.destination || op.destination_path) && (
                        <p className="font-mono text-[12px] text-txt-faint break-all mt-0.5 leading-relaxed">
                            → {op.destination || op.destination_path}
                        </p>
                    )}
                </div>
            ))}
        </div>
    );
}

function DiffsPanel({ task }: { task: any }) {
    const { updateOperationStatus, bulkUpdateOperations } = useStore();

    if (!task) return <EmptyState message="No active task" />;
    if (!task.plan?.operations || task.plan.operations.length === 0) {
        return <EmptyState message="Operations appear after planning" />;
    }

    const DiffViewer = require('../DiffViewer').default;

    return (
        <DiffViewer
            operations={task.plan.operations}
            onUpdateOperation={(opId: string, status: any) =>
                updateOperationStatus(task.id, opId, status)
            }
            onBulkUpdate={(status: any) =>
                bulkUpdateOperations(task.id, status)
            }
            onExecute={() => {
                const { api } = require('@/lib/api/client');
                api.executeTask(task.id).catch(console.error);
            }}
        />
    );
}

function EmptyState({ message }: { message: string }) {
    return (
        <div className="flex items-center justify-center h-full">
            <p className="text-[13px] text-txt-faint">{message}</p>
        </div>
    );
}
