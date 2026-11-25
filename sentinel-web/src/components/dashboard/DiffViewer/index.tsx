'use client';

import { useState, useMemo } from 'react';
import ActionItem, { FileOperation, OperationStatus } from './ActionItem';
import BulkActions from './BulkActions';
import ConfirmationModal from './ConfirmationModal';

interface DiffViewerProps {
    operations: FileOperation[];
    locked: boolean;
    onUpdateOperation: (id: string, status: OperationStatus) => void;
    onBulkUpdate: (status: OperationStatus) => void;
    onExecute: () => void;
}

export default function DiffViewer({
    operations,
    locked,
    onUpdateOperation,
    onBulkUpdate,
    onExecute
}: DiffViewerProps) {
    const [confirmDelete, setConfirmDelete] = useState<FileOperation | null>(null);

    const stats = useMemo(() => {
        const total = operations.length;
        const approved = operations.filter(op => op.status === 'approved').length;
        const rejected = operations.filter(op => op.status === 'rejected').length;
        const pending = operations.filter(op => op.status === 'pending').length;
        return { total, approved, rejected, pending };
    }, [operations]);

    const handleApprove = (id: string) => {
        const op = operations.find(o => o.id === id);
        if (op?.type === 'delete' && op.status !== 'approved') {
            setConfirmDelete(op);
        } else {
            onUpdateOperation(id, 'approved');
        }
    };

    const handleReject = (id: string) => {
        onUpdateOperation(id, 'rejected');
    };

    const handleConfirmDelete = () => {
        if (confirmDelete) {
            onUpdateOperation(confirmDelete.id, 'approved');
            setConfirmDelete(null);
        }
    };

    const handleApproveAll = () => {
        const hasPendingDeletes = operations.some(
            op => op.type === 'delete' && op.status === 'pending'
        );
        if (hasPendingDeletes) {
            const first = operations.find(op => op.type === 'delete' && op.status === 'pending');
            if (first) setConfirmDelete(first);
        } else {
            onBulkUpdate('approved');
        }
    };

    if (operations.length === 0) {
        return (
            <div className="flex items-center justify-center h-full">
                <p className="text-[13px] text-txt-faint">No operations</p>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <BulkActions
                locked={locked}
                totalOperations={stats.total}
                pendingCount={stats.pending}
                approvedCount={stats.approved}
                rejectedCount={stats.rejected}
                onApproveAll={handleApproveAll}
                onRejectAll={() => onBulkUpdate('rejected')}
                onExecute={onExecute}
            />

            <div className="min-w-0 flex-1">
                {operations.map((operation) => (
                    <ActionItem
                        key={operation.id}
                        operation={operation}
                        locked={locked}
                        onApprove={handleApprove}
                        onReject={handleReject}
                    />
                ))}
            </div>

            <ConfirmationModal
                isOpen={confirmDelete !== null}
                fileName={confirmDelete?.source.split('/').pop() || ''}
                filePath={confirmDelete?.source || ''}
                onConfirm={handleConfirmDelete}
                onCancel={() => setConfirmDelete(null)}
            />
        </div>
    );
}
