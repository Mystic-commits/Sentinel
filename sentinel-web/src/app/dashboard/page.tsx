'use client';

import ExecutionHistory from '@/components/dashboard/ExecutionHistory';
import Sidebar from '@/components/dashboard/Sidebar';
import TaskComposer from '@/components/dashboard/TaskComposer';
import Timeline from '@/components/dashboard/Timeline';
import RightPanel from '@/components/dashboard/RightPanel';
import { useActiveTask } from '@/hooks/useStore';

export default function DashboardPage() {
    const activeTask = useActiveTask();

    return (
        <div className="flex min-h-dvh bg-[#0b1312] lg:h-dvh lg:overflow-hidden">
            <div className="hidden lg:block"><Sidebar /></div>
            <main className="min-w-0 flex-1 lg:overflow-y-auto">
                <div className="mx-auto max-w-6xl">
                    <header className="flex items-center justify-between border-b border-edge px-5 py-3 sm:px-8">
                        <h1 className="text-lg font-semibold tracking-tight">File workspace</h1>
                        <span className="rounded-md bg-[#172b21] px-2 py-1 text-xs font-medium text-[#adf1c7]">Local session</span>
                    </header>
                    <TaskComposer />
                    <ExecutionHistory />
                    {activeTask && (
                        <details className="border-b border-edge px-5 py-3 text-sm sm:px-8">
                            <summary className="cursor-pointer">Task progress</summary>
                            <Timeline currentState={activeTask.state} progress={activeTask.progress} />
                        </details>
                    )}
                    <RightPanel />
                </div>
            </main>
        </div>
    );
}
