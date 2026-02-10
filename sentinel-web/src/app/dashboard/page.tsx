'use client';

import Sidebar from '@/components/dashboard/Sidebar';
import TaskComposer from '@/components/dashboard/TaskComposer';
import Timeline from '@/components/dashboard/Timeline';
import RightPanel from '@/components/dashboard/RightPanel';
import { useActiveTask } from '@/hooks/useStore';

export default function DashboardPage() {
    const activeTask = useActiveTask();

    return (
        <div className="flex h-screen bg-surface-0 overflow-hidden">
            <Sidebar />

            {/* Main content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <div className="border-b border-edge">
                    <TaskComposer />
                </div>

                <div className="flex-1 overflow-y-auto">
                    {activeTask ? (
                        <div className="max-w-3xl mx-auto px-8">
                            <Timeline
                                currentState={activeTask.state}
                                progress={activeTask.progress}
                            />
                        </div>
                    ) : (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center space-y-2">
                                <p className="text-[15px] text-txt-muted">
                                    No active task
                                </p>
                                <p className="text-[13px] text-txt-faint">
                                    Describe what you want to organize above
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <RightPanel />
        </div>
    );
}
