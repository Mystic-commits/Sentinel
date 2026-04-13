/**
 * Sidebar Component
 * 
 * Clean left sidebar with logo, nav, and task history.
 */

'use client';

import Link from 'next/link';
import { useStore } from '@/hooks/useStore';
import { STATE_CONFIG } from '@/lib/types/task';

export default function Sidebar() {
    const { tasks, activeTaskId, setActiveTask, sidebarOpen } = useStore();
    const connected = useStore((state) => state.connected);

    if (!sidebarOpen) return null;

    return (
        <aside className="w-60 flex flex-col h-screen bg-[#0a0a0a]">
            {/* Logo */}
            <div className="px-5 py-5 border-b border-[#1f1f1f]">
                <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                        <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                    </div>
                    <div>
                        <h1 className="text-sm font-semibold text-white tracking-wide">Sentinel</h1>
                        <div className="flex items-center gap-1.5 mt-0.5">
                            <div className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                            <span className="text-[10px] text-neutral-500">
                                {connected ? 'Connected' : 'Offline'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="px-3 py-3 border-b border-[#1f1f1f]">
                <NavItem href="/dashboard" label="Home" />
                <NavItem href="/dashboard" label="New Task" />
            </nav>

            {/* Task History */}
            <div className="flex-1 overflow-y-auto px-3 py-3">
                <h2 className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider mb-3 px-2">
                    Recent
                </h2>

                {tasks.length === 0 ? (
                    <p className="text-xs text-neutral-600 px-2 py-4 text-center">
                        No tasks yet
                    </p>
                ) : (
                    <div className="space-y-0.5">
                        {tasks.map((task) => (
                            <TaskHistoryItem
                                key={task.id}
                                task={task}
                                isActive={task.id === activeTaskId}
                                onClick={() => setActiveTask(task.id)}
                            />
                        ))}
                    </div>
                )}
            </div>
        </aside>
    );
}

function NavItem({ href, label }: { href: string; label: string }) {
    return (
        <Link
            href={href}
            className="flex items-center px-3 py-2 rounded-md text-sm text-neutral-400 hover:text-white hover:bg-[#1a1a1a] transition-colors duration-150 mb-0.5"
        >
            {label}
        </Link>
    );
}

function TaskHistoryItem({
    task,
    isActive,
    onClick
}: {
    task: any;
    isActive: boolean;
    onClick: () => void;
}) {
    const stateConfig = STATE_CONFIG[task.state];

    return (
        <button
            onClick={onClick}
            className={`
                w-full text-left px-3 py-2.5 rounded-md transition-colors duration-150
                ${isActive
                    ? 'bg-blue-500/10 text-white'
                    : 'text-neutral-400 hover:bg-[#141414] hover:text-neutral-300'
                }
            `}
        >
            <div className="flex items-center justify-between mb-0.5">
                <span className={`text-[10px] uppercase font-medium tracking-wider ${isActive ? 'text-blue-400' : 'text-neutral-500'}`}>
                    {stateConfig.icon} {stateConfig.label}
                </span>
                <span className="text-[10px] text-neutral-600">
                    {new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
            </div>
            <p className="text-xs line-clamp-1">
                {task.description || 'Untitled'}
            </p>
        </button>
    );
}
