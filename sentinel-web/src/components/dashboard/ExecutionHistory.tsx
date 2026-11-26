'use client';

import { useState } from 'react';
import { api } from '@/lib/api/client';

const stateLabels: Record<string, string> = {
    completed: 'Completed',
    failed: 'Execution failed',
    queued: 'Scheduled · no moves recorded',
    executing: 'Applying moves',
    interrupted: 'Apply interrupted',
    partial: 'Partially applied',
    undoing: 'Restoring files',
    undo_interrupted: 'Restore interrupted',
    restored_with_uncertainty: 'Confirmed files restored · check remaining paths',
    undone: 'Restored',
    undo_failed: 'Undo needs attention',
};

export default function ExecutionHistory() {
    const [receipts, setReceipts] = useState<Awaited<ReturnType<typeof api.history>> | null>(null);
    const [busy, setBusy] = useState(false);
    const [message, setMessage] = useState('');
    const [details, setDetails] = useState<{
        taskId: string;
        entries: Awaited<ReturnType<typeof api.receiptDetails>>;
    } | null>(null);
    const [pendingUndo, setPendingUndo] = useState<string | null>(null);

    async function update(taskId?: string) {
        setBusy(true);
        setMessage('');
        setDetails(null);
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

    async function showDetails(taskId: string) {
        try {
            setDetails({ taskId, entries: await api.receiptDetails(taskId) });
        } catch (error) {
            setMessage(error instanceof Error ? error.message : 'Could not load receipt details.');
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
                <ul className="mt-2 divide-y divide-[#deded8] text-sm">
                    {receipts.map(receipt => (
                        <li key={receipt.task_id} className="flex flex-wrap items-center gap-3 py-2">
                            <span>{receipt.created_at} UTC</span>
                            <span title={receipt.task_id}>{receipt.task_id.slice(0, 13)}</span>
                            <span>{stateLabels[receipt.state] ?? receipt.state}</span>
                            {receipt.operation_count > 0 && (
                                <>
                                    <span>{receipt.applied_count}/{receipt.operation_count} confirmed moved · {receipt.restored_count} restored</span>
                                    <button className="underline" type="button" onClick={() => {
                                        if (details?.taskId === receipt.task_id) setDetails(null);
                                        else void showDetails(receipt.task_id);
                                    }}>{details?.taskId === receipt.task_id ? 'Hide details' : 'Receipt details'}</button>
                                </>
                            )}
                            {(receipt.state === 'completed' || receipt.state === 'partial') && pendingUndo === receipt.task_id ? (
                                <div className="flex flex-wrap items-center gap-2">
                                    <span>Restore the confirmed moves from this task?</span>
                                    <button type="button" className="workspace-secondary"
                                        onClick={() => setPendingUndo(null)}>Cancel</button>
                                    <button type="button" className="workspace-action" disabled={busy}
                                        onClick={() => {
                                            setPendingUndo(null);
                                            void update(receipt.task_id);
                                        }}>Restore files</button>
                                </div>
                            ) : (receipt.state === 'completed' || receipt.state === 'partial') && (
                                <button type="button" disabled={busy} className="underline"
                                    onClick={() => setPendingUndo(receipt.task_id)}>Undo</button>
                            )}
                            {receipt.uncertain_count > 0 && receipt.state !== 'executing' && receipt.state !== 'undoing' && (
                                <p className="w-full font-semibold text-amber-800">
                                    {receipt.uncertain_count} {receipt.uncertain_count === 1 ? 'file needs' : 'files need'} inspection.
                                </p>
                            )}
                            {details?.taskId === receipt.task_id && (
                                <ul className="w-full space-y-2 rounded-lg bg-surface-2 p-3">
                                    {details.entries.map(entry => (
                                        <li key={entry.index} className="break-all">
                                            <p className="font-semibold">
                                                {entry.undo_state === 'done' ? 'Restored'
                                                    : entry.undo_state === 'started' || entry.apply_state === 'started'
                                                        ? (receipt.state === 'executing' || receipt.state === 'undoing' ? 'In progress' : 'Outcome uncertain')
                                                    : entry.apply_state === 'done' ? 'Move confirmed' : 'Move not started'}
                                            </p>
                                            <p className="font-mono text-xs">From {entry.source}</p>
                                            <p className="font-mono text-xs">To {entry.destination}</p>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}
