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
        <div className="min-h-dvh lg:grid lg:grid-cols-[245px_minmax(0,1fr)]">
            <Sidebar />
            <main className="min-w-0">
                <div className="mx-auto max-w-6xl px-4 pb-10 sm:px-8">
                    <header className="flex items-center justify-between gap-3 py-5 sm:py-7">
                        <h1 className="text-3xl font-extrabold tracking-[-0.055em]">File workspace</h1>
                    </header>
                    <details open={activeTask?.state !== 'review'} className="mb-2">
                        <summary className="mb-2 cursor-pointer text-sm font-bold">Scan a folder</summary>
                        <TaskComposer />
                    </details>
                    <div className="mb-5"><ExecutionHistory /></div>
                    {activeTask && (
                        <details className="mb-4 text-sm text-txt-secondary">
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
