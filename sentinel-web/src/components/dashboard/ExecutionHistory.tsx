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
        <section aria-label="Execution history" className="border-b border-edge px-8 py-3">
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
                            {receipt.state === 'completed' && (
                                <button
                                    type="button"
                                    disabled={busy}
                                    className="underline"
                                    onClick={() => {
                                        if (window.confirm('Restore the files moved by this task?')) void update(receipt.task_id);
                                    }}
                                >
                                    Undo
                                </button>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}
