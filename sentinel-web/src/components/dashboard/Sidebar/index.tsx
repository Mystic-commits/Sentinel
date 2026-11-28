'use client';

import SiteMark from '@/components/landing/SiteMark';
import { useStore } from '@/hooks/useStore';
import { STATE_CONFIG } from '@/lib/types/task';

function folderName(path: string) {
    return path.split(/[/\\]/).filter(Boolean).at(-1) || path;
}

export default function Sidebar() {
    const { tasks, activeTaskId, setActiveTask, connected } = useStore();

    return (
        <aside className="flex flex-col border-b border-edge bg-[#f0f0eb] p-4 lg:sticky lg:top-0 lg:h-dvh lg:border-b-0 lg:border-r">
            <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5 text-lg font-extrabold tracking-tight"><SiteMark />Sentinel</div>
                <span className={`text-xs font-bold ${connected ? 'text-green-800' : 'text-red-700'}`}>
                    {connected ? 'Local' : 'Offline'}
                </span>
            </div>
            <label className="mt-3 flex items-center gap-2 text-sm font-semibold lg:hidden">
                Task
                <select value={activeTaskId ?? ''} disabled={!tasks.length} onChange={event => setActiveTask(event.target.value)}
                    className="workspace-input min-w-0 flex-1 truncate px-2 py-2 text-base">
                    <option value="" disabled>No active task</option>
                    {tasks.map(task => <option key={task.id} value={task.id}>{folderName(task.description)}</option>)}
                </select>
            </label>
            <div className="mt-8 hidden min-h-0 flex-1 overflow-y-auto lg:block">
                <h2 className="mb-3 text-sm font-extrabold">Recent tasks</h2>
                {tasks.length === 0 && <p className="text-sm text-txt-secondary">Scans appear here as you work.</p>}
                <ul className="space-y-2">
                    {tasks.map(task => (
                        <li key={task.id}>
                            <button type="button" onClick={() => setActiveTask(task.id)} aria-current={task.id === activeTaskId ? 'true' : undefined}
                                className={`w-full rounded-lg px-3 py-2.5 text-left ${task.id === activeTaskId ? 'bg-[#e2e6fa] text-[#1e319f]' : 'hover:bg-white'}`}>
                                <span className="block truncate text-sm font-extrabold" title={task.description}>{folderName(task.description)}</span>
                                <span className="text-xs text-txt-secondary">{STATE_CONFIG[task.state].label}</span>
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
        </aside>
    );
}
