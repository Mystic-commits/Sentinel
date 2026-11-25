'use client';

interface BulkActionsProps {
    locked: boolean;
    totalOperations: number;
    pendingCount: number;
    approvedCount: number;
    rejectedCount: number;
    onApproveAll: () => void;
    onRejectAll: () => void;
    onExecute: () => void;
}

export default function BulkActions({
    locked,
    totalOperations,
    pendingCount,
    approvedCount,
    rejectedCount,
    onApproveAll,
    onRejectAll,
    onExecute,
}: BulkActionsProps) {
    return (
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-edge p-3 sm:px-5">
            <p className="text-sm text-txt-secondary">
                <strong className="text-txt-primary">{totalOperations} proposed</strong>
                {' · '}{pendingCount} pending · {approvedCount} approved · {rejectedCount} kept
            </p>
            <div className="flex flex-wrap gap-2">
                <button type="button" className="workspace-secondary workspace-bulk" onClick={onApproveAll} disabled={locked || !pendingCount}>Approve pending</button>
                <button type="button" className="workspace-secondary workspace-bulk" onClick={onRejectAll} disabled={locked || !pendingCount}>Keep pending files</button>
                <button type="button" className="workspace-action" onClick={onExecute} disabled={locked || !approvedCount}>
                    Apply {approvedCount} {approvedCount === 1 ? 'move' : 'moves'}
                </button>
            </div>
        </div>
    );
}
