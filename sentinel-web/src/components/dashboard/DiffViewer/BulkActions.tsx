'use client';

interface BulkActionsProps {
    totalOperations: number;
    pendingCount: number;
    approvedCount: number;
    rejectedCount: number;
    onApproveAll: () => void;
    onRejectAll: () => void;
    onExecute: () => void;
}

export default function BulkActions({
    totalOperations,
    pendingCount,
    approvedCount,
    rejectedCount,
    onApproveAll,
    onRejectAll,
    onExecute,
}: BulkActionsProps) {
    return (
        <div className="sticky top-0 bg-surface-1 border-b border-edge p-3 z-20">
            {/* Stats */}
            <div className="flex items-center gap-3 text-[12px] font-mono mb-3">
                <span className="text-txt-muted">{totalOperations} total</span>
                {pendingCount > 0 && (
                    <span className="text-txt-secondary">{pendingCount} pending</span>
                )}
                {approvedCount > 0 && (
                    <span className="text-emerald-400">{approvedCount} approved</span>
                )}
                {rejectedCount > 0 && (
                    <span className="text-red-400">{rejectedCount} rejected</span>
                )}
            </div>

            {/* Actions */}
            <div className="flex gap-2">
                <button
                    onClick={onApproveAll}
                    disabled={pendingCount === 0}
                    className="
                        flex-1 h-8 rounded-lg text-[12px] font-medium
                        bg-surface-2 text-txt-primary border border-edge
                        hover:bg-surface-3 hover:border-edge-hover
                        disabled:opacity-25 disabled:cursor-not-allowed
                        transition-colors
                    "
                >
                    Approve{pendingCount > 0 ? ` (${pendingCount})` : ''}
                </button>
                <button
                    onClick={onRejectAll}
                    disabled={pendingCount === 0}
                    className="
                        flex-1 h-8 rounded-lg text-[12px] font-medium
                        text-txt-muted border border-edge
                        hover:text-txt-secondary hover:border-edge-hover
                        disabled:opacity-25 disabled:cursor-not-allowed
                        transition-colors
                    "
                >
                    Reject
                </button>
                <button
                    onClick={onExecute}
                    disabled={approvedCount === 0}
                    className="
                        flex-1 h-8 rounded-lg text-[12px] font-semibold
                        bg-white text-black
                        hover:bg-neutral-200
                        disabled:opacity-25 disabled:cursor-not-allowed
                        transition-colors
                    "
                >
                    Run ({approvedCount})
                </button>
            </div>
        </div>
    );
}
