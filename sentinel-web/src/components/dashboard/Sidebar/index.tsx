'use client';

import Link from 'next/link';
import { useStore } from '@/hooks/useStore';
import { STATE_CONFIG } from '@/lib/types/task';

export default function Sidebar() {
    const { tasks, activeTaskId, setActiveTask, sidebarOpen } = useStore();
    const connected = useStore((state) => state.connected);

    if (!sidebarOpen) return null;

    return (
        <aside className="w-64 flex flex-col h-screen bg-surface-1 border-r border-edge">
            {/* Brand */}
            <div className="px-5 h-14 flex items-center gap-3 border-b border-edge">
                <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
                    <span className="text-sm font-bold text-black tracking-tight">S</span>
                </div>
                <div className="flex-1">
                    <span className="text-[15px] font-semibold text-txt-primary tracking-[-0.02em]">
                        Sentinel
                    </span>
                </div>
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'}`} />
            </div>

            {/* Nav */}
            <nav className="px-3 py-3 border-b border-edge">
                <Link
                    href="/dashboard"
                    className="flex items-center gap-2.5 h-9 px-3 rounded-lg text-[14px] text-txt-secondary hover:text-txt-primary hover:bg-surface-2 transition-colors"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>
                    New task
                </Link>
            </nav>

            {/* History */}
            <div className="flex-1 overflow-y-auto px-3 py-3">
                <p className="text-[11px] font-semibold text-txt-faint uppercase tracking-[0.1em] px-3 mb-2">
                    History
                </p>

                {tasks.length === 0 ? (
                    <p className="text-[13px] text-txt-muted px-3 py-8 text-center">
                        No tasks yet
                    </p>
                ) : (
                    <div className="space-y-1">
                        {tasks.map((task) => {
                            const isActive = task.id === activeTaskId;
                            const cfg = STATE_CONFIG[task.state];
                            return (
                                <button
                                    key={task.id}
                                    onClick={() => setActiveTask(task.id)}
                                    className={`
                                        w-full text-left px-3 py-2.5 rounded-lg transition-colors
                                        ${isActive
                                            ? 'bg-surface-2 text-txt-primary'
                                            : 'text-txt-secondary hover:bg-surface-2/50 hover:text-txt-primary'
                                        }
                                    `}
                                >
                                    <div className="flex items-center justify-between mb-0.5">
                                        <span className={`text-[11px] font-medium uppercase tracking-wider ${cfg.color}`}>
                                            {cfg.label}
                                        </span>
                                        <span className="text-[11px] text-txt-faint">
                                            {new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                    <p className="text-[13px] line-clamp-1 leading-snug">
                                        {task.description || 'Untitled'}
                                    </p>
                                </button>
                            );
                        })}
                    </div>
                )}
            </div>
        </aside>
    );
}
