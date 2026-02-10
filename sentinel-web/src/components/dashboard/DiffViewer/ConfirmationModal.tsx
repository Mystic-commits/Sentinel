'use client';

interface ConfirmationModalProps {
    isOpen: boolean;
    fileName: string;
    filePath: string;
    onConfirm: () => void;
    onCancel: () => void;
}

export default function ConfirmationModal({
    isOpen,
    fileName,
    filePath,
    onConfirm,
    onCancel,
}: ConfirmationModalProps) {
    if (!isOpen) return null;

    return (
        <>
            <div onClick={onCancel} className="fixed inset-0 bg-black/70 z-40" />

            <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
                <div className="bg-surface-2 border border-edge rounded-xl max-w-md w-full p-6 animate-fade-in">
                    <h3 className="text-[16px] font-semibold text-txt-primary mb-2">
                        Delete this file?
                    </h3>

                    <p className="text-[14px] text-txt-secondary mb-4">
                        This operation will permanently remove the file.
                    </p>

                    <div className="bg-surface-0 rounded-lg p-3 mb-4 border border-edge">
                        <p className="text-[13px] text-txt-primary font-medium break-all">
                            {fileName}
                        </p>
                        <p className="text-[12px] text-txt-muted font-mono mt-1 break-all">
                            {filePath}
                        </p>
                    </div>

                    <p className="text-[13px] text-txt-muted mb-5">
                        The file will be moved to trash and can be restored.
                    </p>

                    <div className="flex gap-3">
                        <button
                            onClick={onCancel}
                            className="flex-1 h-10 rounded-lg text-[13px] font-medium text-txt-secondary bg-surface-3 border border-edge hover:bg-surface-3/80 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={onConfirm}
                            className="flex-1 h-10 rounded-lg text-[13px] font-semibold text-white bg-red-600 hover:bg-red-500 transition-colors"
                        >
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}
