'use client';

import DiffViewer from '../DiffViewer';
import type { OperationStatus } from '../DiffViewer/ActionItem';
import { api } from '@/lib/api/client';

import { useStore, useActiveTask } from '@/hooks/useStore';
import { LogEntry } from '@/lib/types/task';
import { useEffect, useRef, useState } from 'react';

type Tab = 'logs' | 'preview' | 'diffs';

const TABS: Tab[] = ['diffs', 'preview', 'logs'];

export default function RightPanel() {
    const { activePanel, setActivePanel } = useStore();
    const activeTask = useActiveTask();

    return (
        <div className="workspace-panel flex min-h-56 min-w-0 flex-col">
            {/* Tabs */}
            <div className="flex gap-1 border-b border-edge px-2 sm:px-4">
                {TABS.map((tab) => (
                    <button
                        key={tab}
                        aria-pressed={activePanel === tab}
                        onClick={() => setActivePanel(tab)}
                        className="workspace-tab px-3 py-3 text-sm font-bold text-txt-secondary"
                    >
                        {tab === 'diffs' ? 'Review' : tab === 'logs' ? 'Activity' : 'Preview'}
                    </button>
                ))}
            </div>

            {activeTask?.plan?.planningSource && (
                <p className="border-b border-edge px-3 py-2 text-sm text-txt-secondary sm:px-5">
                    Plan from {activeTask.plan.planningSource === 'ai' ? 'local AI' : 'local rules'}
                </p>
            )}

            {/* Content */}
            <div className="min-w-0 flex-1">
                {activePanel === 'logs' && <LogsPanel task={activeTask} />}
                {activePanel === 'preview' && <PreviewPanel task={activeTask} />}
                {activePanel === 'diffs' && <DiffsPanel key={activeTask?.id} task={activeTask} />}
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
        return <EmptyState message="Scan a folder to review its proposed moves." />;
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
        success: 'text-green-800',
        warning: 'text-amber-800',
        error: 'text-red-700',
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
    const { updateOperationStatus, bulkUpdateOperations, updateTask } = useStore();
    const [error, setError] = useState<string | null>(null);
    const [applying, setApplying] = useState(false);

    if (!task) return <EmptyState message="Scan a folder to review its proposed moves." />;
    if (task.state === 'failed') return <EmptyState message="Task failed. Open Activity for details and check execution history for any recorded moves." />;
    if (!task.plan?.operations || task.plan.operations.length === 0) {
        return <EmptyState message={task.state === "review" ? "No moves were proposed for this folder." : "Proposed moves will appear here when planning finishes."} />;
    }


    return (
        <>
        {error && <p role="alert" className="p-3 text-sm text-red-700">{error}</p>}
        <DiffViewer
            operations={task.plan.operations}
            locked={applying || task.state !== 'review'}
            onUpdateOperation={(opId: string, status: OperationStatus) =>
                updateOperationStatus(task.id, opId, status)
            }
            onBulkUpdate={(status: OperationStatus) =>
                bulkUpdateOperations(task.id, status)
            }
            onExecute={async () => {
                if (applying || task.state !== 'review') return;
                const approved = task.plan.operations.flatMap(
                    (operation: { status: string }, index: number) => operation.status === 'approved' ? [index] : []
                );
                setError(null);
                setApplying(true);
                try {
                    await api.executeTask(task.id, approved);
                    if (useStore.getState().tasks.find(item => item.id === task.id)?.state === 'review') {
                        updateTask(task.id, { state: 'executing' });
                    }
                } catch (error) {
                    setError(error instanceof Error ? error.message : 'Could not apply moves.');
                } finally {
                    setApplying(false);
                }
            }}
        />
        </>
    );
}

function EmptyState({ message }: { message: string }) {
    return (
        <div className="flex min-h-36 items-center justify-center px-5 text-center">
            <p className="text-[13px] text-txt-faint">{message}</p>
        </div>
    );
}
