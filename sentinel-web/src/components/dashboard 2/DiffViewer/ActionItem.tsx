/**
 * Action Item Component
 * 
 * Single file operation row with approve/reject controls.
 */

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

const OP_CONFIG = {
    move: { label: 'MOVE', color: 'text-blue-400' },
    delete: { label: 'DELETE', color: 'text-red-400' },
    rename: { label: 'RENAME', color: 'text-amber-400' },
    create: { label: 'CREATE', color: 'text-green-400' },
};

export default function ActionItem({ operation, onApprove, onReject }: ActionItemProps) {
    const [showReason, setShowReason] = useState(false);
    const config = OP_CONFIG[operation.type];

    const borderColor = operation.status === 'approved'
        ? 'border-green-500/20'
        : operation.status === 'rejected'
            ? 'border-red-500/20'
            : 'border-[#1f1f1f]';

    const bgColor = operation.status === 'approved'
        ? 'bg-green-500/5'
        : operation.status === 'rejected'
            ? 'bg-red-500/5'
            : 'bg-[#141414]';

    return (
        <div className={`p-3 rounded-lg border ${borderColor} ${bgColor} transition-colors duration-150`}>
            <div className="flex items-start gap-3">
                {/* Toggle */}
                <ActionToggle
                    status={operation.status}
                    onApprove={() => onApprove(operation.id)}
                    onReject={() => onReject(operation.id)}
                />

                {/* Content */}
                <div className="flex-1 min-w-0">
                    {/* Type */}
                    <div className="flex items-center gap-2 mb-1">
                        <span className={`text-[10px] font-semibold ${config.color}`}>
                            {config.label}
                        </span>
                        {operation.type === 'delete' && (
                            <span className="text-[10px] text-red-400">⚠ destructive</span>
                        )}
                    </div>

                    {/* Paths */}
                    <p className="font-mono text-xs text-neutral-300 break-all">
                        {operation.source}
                    </p>
                    {operation.destination && (
                        <p className="font-mono text-xs text-blue-400 break-all mt-0.5">
                            <span className="text-neutral-600">→ </span>
                            {operation.destination}
                        </p>
                    )}

                    {/* Size */}
                    {operation.size && (
                        <p className="text-[10px] text-neutral-600 mt-1">{formatBytes(operation.size)}</p>
                    )}

                    {/* Reason toggle */}
                    {operation.reason && (
                        <>
                            <button
                                onClick={() => setShowReason(!showReason)}
                                className="mt-2 text-[10px] text-neutral-500 hover:text-neutral-300 transition-colors"
                            >
                                {showReason ? '▼' : '▶'} Why?
                            </button>
                            {showReason && (
                                <div className="mt-1 p-2 bg-[#0a0a0a] rounded border border-[#1f1f1f]">
                                    <p className="text-[11px] text-neutral-500 leading-relaxed">{operation.reason}</p>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

function formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
