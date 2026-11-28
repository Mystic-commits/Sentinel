'use client';

import { Check, X } from 'lucide-react';

interface ActionToggleProps {
    status: 'pending' | 'approved' | 'rejected';
    name: string;
    disabled: boolean;
    onApprove: () => void;
    onReject: () => void;
}

export default function ActionToggle({ status, name, disabled, onApprove, onReject }: ActionToggleProps) {
    return (
        <div className="flex items-center gap-2">
            <button type="button" disabled={disabled} aria-label={`Approve ${name}`} aria-pressed={status === 'approved'}
                onClick={onApprove} className="workspace-secondary workspace-decision">
                <Check size={15} aria-hidden /> Approve
            </button>
            <button type="button" disabled={disabled} aria-label={`Keep ${name} in place`} aria-pressed={status === 'rejected'}
                onClick={onReject} className="workspace-secondary workspace-decision">
                <X size={15} aria-hidden /> Keep
            </button>
        </div>
    );
}
