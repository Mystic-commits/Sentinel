'use client';

import { FormEvent, useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { useStore } from '@/hooks/useStore';
import { api } from '@/lib/api/client';

export default function TaskComposer() {
    const [folder, setFolder] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { addTask } = useStore();

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const path = folder.trim();
        if (!path || isSubmitting) return;
        setError(null);
        setIsSubmitting(true);

        try {
            const response = await api.createPlan(null, 'file_organization', undefined, path);
            const now = new Date().toISOString();
            addTask({
                id: response.task_id,
                description: path,
                mode: 'file_organization',
                state: 'planning',
                created_at: now,
                updated_at: now,
                logs: [],
            });
        } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to create task');
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} className="border-b border-edge px-5 py-5 sm:px-8">
            <label htmlFor="folder-path" className="mb-2 block text-sm font-semibold">Folder path</label>
            <div className="flex flex-col gap-3 sm:flex-row">
                <div className="flex min-w-0 flex-1 items-center gap-3 rounded-lg border border-[#405349] bg-[#111d18] px-3">
                    <FolderOpen size={18} className="shrink-0 text-[#a6edc3]" aria-hidden />
                    <input id="folder-path" type="text" required value={folder} autoComplete="off"
                        onChange={event => setFolder(event.target.value)}
                        className="min-w-0 flex-1 bg-transparent px-1 py-3 text-base text-[#edf6ef]" />
                </div>
                <button type="submit" disabled={!folder.trim() || isSubmitting}
                    className="rounded-lg bg-[#a6edc3] px-4 py-3 text-sm font-semibold text-[#12241c] disabled:opacity-60">
                    {isSubmitting ? 'Starting scan…' : 'Scan and plan'}
                </button>
            </div>
            {error && <p role="alert" className="mt-3 text-sm text-red-300">{error}</p>}
        </form>
    );
}
