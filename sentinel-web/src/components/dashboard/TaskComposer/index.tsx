'use client';

import { FormEvent, useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { useStore } from '@/hooks/useStore';
import { api } from '@/lib/api/client';

export default function TaskComposer() {
    const [useAi, setUseAi] = useState(false);
    const [prompt, setPrompt] = useState('');
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
            const response = await api.createPlan(path, useAi, useAi ? prompt.trim() : undefined);
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
        <form onSubmit={handleSubmit} className="workspace-panel mb-3 p-4 sm:p-5">
            <label htmlFor="folder-path" className="mb-2 block text-sm font-semibold">Absolute folder path</label>
            <div className="flex flex-col gap-3 sm:flex-row">
                <div className="flex min-w-0 flex-1 items-center gap-3 workspace-input px-3">
                    <FolderOpen size={18} className="shrink-0 text-[#263bc0]" aria-hidden />
                    <input id="folder-path" type="text" required value={folder} autoComplete="off"
                        onChange={event => setFolder(event.target.value)}
                        className="min-w-0 flex-1 bg-transparent px-1 py-3 text-base text-[#141721]" />
                </div>
                <button type="submit" disabled={!folder.trim() || isSubmitting}
                    className="workspace-action">
                    {isSubmitting ? 'Starting scan…' : 'Scan and plan'}
                </button>
            </div>
            <label className="mt-3 flex items-center gap-2 text-sm font-semibold">
                <input type="checkbox" checked={useAi} disabled={isSubmitting}
                    onChange={event => setUseAi(event.target.checked)} className="size-4 accent-[#263bc0]" />
                Use local AI (Ollama)
            </label>
            {useAi && (
                <label className="mt-3 grid gap-2 text-sm font-semibold">
                    Instructions (optional)
                    <textarea value={prompt} onChange={event => setPrompt(event.target.value)}
                        maxLength={1000} rows={2} className="workspace-input p-3 text-base font-normal" />
                </label>
            )}
            {error && <p role="alert" className="mt-3 text-sm text-red-700">{error}</p>}
        </form>
    );
}
