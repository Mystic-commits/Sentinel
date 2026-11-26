'use client';

import { useState } from 'react';
import { api } from '@/lib/api/client';

const stateLabels: Record<string, string> = {
    completed: 'Completed',
    failed: 'Execution failed',
    executing: 'In progress or interrupted',
    undoing: 'Undo in progress or interrupted',
    undone: 'Restored',
    undo_failed: 'Undo needs attention',
};

export default function ExecutionHistory() {
    const [receipts, setReceipts] = useState<Awaited<ReturnType<typeof api.history>> | null>(null);
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState('');
    const [pendingUndo, setPendingUndo] = useState<string | null>(null);

    async function update(taskId?: string) {
        setBusy(true);
        setMessage('');
        try {
            if (taskId) {
                const result = await api.undoTask(taskId);
                setMessage(result.message);
            }
            const history = await api.history();
            setReceipts(history);
        } catch (error) {
            setMessage(error instanceof Error ? error.message : 'Could not load execution history.');
        } finally {
            setBusy(false);
        }
    }

    return (
        <section aria-label="Execution history" className="px-1 py-2">
            <button className="text-sm underline" disabled={busy} onClick={() => void update()}>
                {receipts ? 'Refresh execution history' : 'Show execution history'}
            </button>
            {message && <p role="status" className="mt-2 text-sm">{message}</p>}
            {receipts?.length === 0 && <p className="mt-2 text-sm">No recorded executions.</p>}
            {receipts && receipts.length > 0 && (
                <ul className="mt-2 max-h-44 overflow-y-auto text-sm">
                    {receipts.map(receipt => (
                        <li key={receipt.task_id} className="flex flex-wrap items-center gap-3 py-2">
                            <span>{receipt.created_at} UTC</span>
                            <span title={receipt.task_id}>{receipt.task_id.slice(0, 13)}</span>
                            <span>{stateLabels[receipt.state] ?? receipt.state}</span>
                            {receipt.state === 'completed' && pendingUndo === receipt.task_id ? (
                                <div className="flex flex-wrap items-center gap-2">
                                    <span>Restore the files moved by this task?</span>
                                    <button type="button" className="workspace-secondary"
                                        onClick={() => setPendingUndo(null)}>Cancel</button>
                                    <button type="button" className="workspace-action" disabled={busy}
                                        onClick={() => {
                                            setPendingUndo(null);
                                            void update(receipt.task_id);
                                        }}>Restore files</button>
                                </div>
                            ) : receipt.state === 'completed' && (
                                <button type="button" disabled={busy} className="underline"
                                    onClick={() => setPendingUndo(receipt.task_id)}>Undo</button>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}
