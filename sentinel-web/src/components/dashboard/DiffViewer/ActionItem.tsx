'use client';

import { ArrowRight, FileText } from 'lucide-react';
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
    locked: boolean;
    onApprove: (id: string) => void;
    onReject: (id: string) => void;
}

export default function ActionItem({ operation, locked, onApprove, onReject }: ActionItemProps) {
    const name = operation.source.split(/[/\\]/).filter(Boolean).at(-1) ?? operation.source;
    const destination = operation.destination?.split(/[/\\]/).filter(Boolean).slice(-2).join('/');
    const decision = { pending: 'Pending', approved: 'Approved', rejected: 'Keep in place' }[operation.status];

    return (
        <article className="border-b border-edge px-3 py-4 last:border-b-0 sm:px-5">
            <div className="flex min-w-0 flex-wrap items-center justify-between gap-3">
                <div className="flex min-w-0 flex-1 items-center gap-3">
                    <div className="rounded-lg bg-[#eef0fa] p-2 text-[#263bc0]"><FileText size={17} aria-hidden /></div>
                    <div className="min-w-0">
                        <p className="break-all text-sm font-extrabold">{name}</p>
                        <p className="mt-0.5 text-xs text-txt-secondary">{decision}</p>
                    </div>
                </div>
                <ActionToggle disabled={locked} name={name} status={operation.status}
                    onApprove={() => onApprove(operation.id)} onReject={() => onReject(operation.id)} />
            </div>
            {destination && (
                <p className="mt-2 flex items-center gap-2 break-all font-mono text-xs text-[#263bc0]">
                    <ArrowRight size={14} className="shrink-0" aria-hidden /> {destination}
                </p>
            )}
            <details className="mt-2 text-xs text-txt-secondary">
                <summary className="cursor-pointer font-bold">File details</summary>
                <p className="mt-2 break-all font-mono">From {operation.source}</p>
                {operation.destination && <p className="mt-1 break-all font-mono">To {operation.destination}</p>}
                {operation.reason && <p className="mt-2">{operation.reason}</p>}
            </details>
        </article>
    );
}
