'use client';

import { useState } from 'react';
import ActionToggle from './ActionToggle';

export type OperationStatus = 'pending' | 'approved' | 'rejected';

export interface FileOperation {
    id: string;
    type: 'move' | 'delete' | 'rename' | 'create';
    source: string;
    destination?: string;
    reason?: string;
    status: OperationStatus;
    size?: number;
}

interface ActionItemProps {
    operation: FileOperation;
    onApprove: (id: string) => void;
    onReject: (id: string) => void;
}

export default function ActionItem({ operation, onApprove, onReject }: ActionItemProps) {
    const [expanded, setExpanded] = useState(false);

    const statusBorder =
        operation.status === 'approved' ? 'border-l-emerald-400' :
            operation.status === 'rejected' ? 'border-l-red-400' :
                'border-l-transparent';

    return (
        <div className={`border-l-2 ${statusBorder} pl-3 py-2 transition-colors`}>
            <div className="flex items-start gap-2.5">
                <ActionToggle
                    status={operation.status}
                    onApprove={() => onApprove(operation.id)}
                    onReject={() => onReject(operation.id)}
                />

                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-[11px] font-semibold text-txt-secondary uppercase tracking-wider">
                            {operation.type}
                        </span>
                        {operation.type === 'delete' && (
                            <span className="text-[10px] text-red-400/60 font-medium px-1.5 py-0.5 rounded bg-red-500/5">
                                destructive
                            </span>
                        )}
                    </div>

                    <p className="font-mono text-[12px] text-txt-secondary break-all leading-relaxed">
                        {operation.source}
                    </p>
                    {operation.destination && (
                        <p className="font-mono text-[12px] text-txt-muted break-all leading-relaxed">
                            <span className="text-txt-faint">→ </span>
                            {operation.destination}
                        </p>
                    )}

                    {operation.reason && (
                        <button
                            onClick={() => setExpanded(!expanded)}
                            className="text-[11px] text-txt-faint hover:text-txt-muted mt-1.5 transition-colors"
                        >
                            {expanded ? '− hide reason' : '+ reason'}
                        </button>
                    )}
                    {expanded && operation.reason && (
                        <p className="text-[12px] text-txt-muted mt-1 leading-relaxed bg-surface-2 rounded px-2 py-1.5">
                            {operation.reason}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
