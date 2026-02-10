'use client';

type OperationStatus = 'pending' | 'approved' | 'rejected';

interface ActionToggleProps {
    status: OperationStatus;
    onApprove: () => void;
    onReject: () => void;
    disabled?: boolean;
}

export default function ActionToggle({
    status,
    onApprove,
    onReject,
    disabled = false,
}: ActionToggleProps) {
    return (
        <div className="flex items-center gap-1 mt-0.5">
            <button
                onClick={onApprove}
                disabled={disabled || status === 'approved'}
                className={`
                    w-5 h-5 rounded flex items-center justify-center transition-colors
                    ${status === 'approved'
                        ? 'bg-emerald-500/15 text-emerald-400'
                        : 'bg-surface-2 text-txt-faint hover:text-emerald-400 hover:bg-emerald-500/10'
                    }
                    ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
                `}
            >
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 13l4 4L19 7" />
                </svg>
            </button>

            <button
                onClick={onReject}
                disabled={disabled || status === 'rejected'}
                className={`
                    w-5 h-5 rounded flex items-center justify-center transition-colors
                    ${status === 'rejected'
                        ? 'bg-red-500/15 text-red-400'
                        : 'bg-surface-2 text-txt-faint hover:text-red-400 hover:bg-red-500/10'
                    }
                    ${disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
                `}
            >
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
    );
}
