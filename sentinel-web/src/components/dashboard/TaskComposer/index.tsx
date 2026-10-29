'use client';

import { useState } from 'react';
import { useStore } from '@/hooks/useStore';
import { api } from '@/lib/api/client';

const suggestions = ['Group my files into clear folders', 'Help me review old installers', 'Organize screenshots and documents'];

export default function TaskComposer() {
    const [description, setDescription] = useState('');
    const [path, setPath] = useState('');
    const [advanced, setAdvanced] = useState(false);
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const addTask = useStore(state => state.addTask);
    const connected = useStore(state => state.connected);

    const handleSubmit = async () => {
        if (!description.trim() || !path.trim() || isSubmitting) return;
        setIsSubmitting(true);
        setError('');
        try {
            const response = await api.createPlan(null, 'file_organization', description.trim(), path.trim()) as {task_id: string};
            const now = new Date().toISOString();
            addTask({id: response.task_id, description, path, mode: 'file_organization', state: 'planning', created_at: now, updated_at: now,
                logs: [{id: crypto.randomUUID(), message: 'Creating your preview. Files have not been changed.', timestamp: now, level: 'info'}]});
            setDescription('');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Could not create a preview. Check that the local agent is running.');
        } finally { setIsSubmitting(false); }
    };

    return (
        <section className="px-5 sm:px-8 py-6 max-w-3xl mx-auto w-full" aria-label="Create an organization preview">
            <div className="flex items-center justify-between gap-3 mb-4">
                <div><h1 className="text-xl font-semibold">Make room for what matters.</h1><p className="text-sm text-txt-muted mt-1">Tell Sentinel what you need. You review every change.</p></div>
                <span className="text-xs text-txt-muted" role="status">{connected ? 'Agent connected' : 'Agent disconnected'}</span>
            </div>
            <div className="bg-surface-2 border border-edge rounded-xl p-4 space-y-4">
                <div>
                    <label htmlFor="folder" className="block text-sm font-medium mb-2">1. Choose the folder to work in</label>
                    <input id="folder" value={path} onChange={e => setPath(e.target.value)} placeholder="Paste a full folder path" autoComplete="off" className="w-full rounded-lg bg-surface-1 border border-edge px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400" aria-describedby="folder-help" />
                    <p id="folder-help" className="text-xs text-txt-muted mt-2">Copy a folder’s path from Finder or File Explorer. Only this folder is included.</p>
                </div>
                <div>
                    <label htmlFor="goal" className="block text-sm font-medium mb-2">2. What would you like to organize?</label>
                    <textarea id="goal" value={description} onChange={e => setDescription(e.target.value)} rows={3} placeholder="For example: group my PDFs by topic and leave my photos alone" className="w-full bg-transparent text-sm resize-y focus:outline-none focus:ring-2 focus:ring-cyan-400 rounded p-2" onKeyDown={e => {if(e.key === 'Enter' && (e.metaKey || e.ctrlKey)){e.preventDefault(); void handleSubmit();}}} />
                    <div className="flex flex-wrap gap-2 mt-2">{suggestions.map(item => <button type="button" key={item} onClick={() => setDescription(item)} className="text-xs rounded-full px-3 py-2 border border-edge hover:bg-surface-3">{item}</button>)}</div>
                </div>
                {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-edge">
                    <p className="text-xs text-txt-muted">Preview first · Approve selected changes · View results</p>
                    <button onClick={() => void handleSubmit()} disabled={!description.trim() || !path.trim() || isSubmitting || !connected} className="px-5 py-2.5 rounded-lg bg-white text-black text-sm font-semibold disabled:opacity-40">{isSubmitting ? 'Preparing preview…' : 'Create preview'}</button>
                </div>
            </div>
            <button className="text-xs text-txt-muted mt-4 underline underline-offset-4" aria-expanded={advanced} onClick={() => setAdvanced(!advanced)}>Prefer the terminal? Open advanced access</button>
            {advanced && <div className="mt-3 rounded-xl border border-edge p-4 text-sm space-y-3"><p>Use the same local agent from an interactive terminal session.</p><code className="block overflow-x-auto bg-surface-2 p-3 rounded">sentinel-shell</code><p className="text-txt-muted">Set a folder with <code>/folder</code>, describe a goal, then use <code>/review</code> and <code>/apply 1,3</code>. Execution requires a typed confirmation.</p><p className="text-xs text-txt-muted">The local API must be running. Command-line setup is in the project README.</p></div>}
            {!connected && <p className="text-sm text-amber-400 mt-3" role="status">Start the Sentinel local agent to create a preview. Your draft stays here while it connects.</p>}
        </section>
    );
}
