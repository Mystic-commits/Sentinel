'use client';

import { STATE_CONFIG, TaskState } from '@/lib/types/task';

const STEPS: TaskState[] = ['scanning', 'planning', 'review', 'executing', 'completed'];

interface TimelineProps {
    currentState: TaskState;
    progress?: number;
}

export default function Timeline({ currentState, progress = 0 }: TimelineProps) {
    const currentIndex = STEPS.indexOf(currentState);
    const isFailed = currentState === 'failed';

    return (
        <div className="py-10">
            {/* Stepper */}
            <div className="bg-surface-2 border border-edge rounded-xl p-6">
                <div className="relative flex items-center justify-between">
                    {/* Track line */}
                    <div className="absolute top-3 left-0 right-0 h-[2px] bg-edge" />
                    <div
                        className="absolute top-3 left-0 h-[2px] transition-all duration-700 ease-out rounded-full"
                        style={{
                            width: isFailed ? '0%' : `${Math.max(0, (currentIndex / (STEPS.length - 1)) * 100)}%`,
                            background: '#ededed',
                        }}
                    />

                    {STEPS.map((step, i) => {
                        const isActive = i === currentIndex;
                        const isDone = i < currentIndex;
                        const config = STATE_CONFIG[step];

                        return (
                            <div key={step} className="relative flex flex-col items-center z-10">
                                <div
                                    className={`
                                        w-6 h-6 rounded-full transition-all duration-300 flex items-center justify-center
                                        ${isDone
                                            ? 'bg-txt-primary'
                                            : isActive
                                                ? 'bg-surface-0 border-2 border-txt-primary'
                                                : 'bg-surface-0 border-2 border-edge'
                                        }
                                    `}
                                >
                                    {isDone && (
                                        <svg className="w-3 h-3 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                    {isActive && (
                                        <div className="w-2 h-2 rounded-full bg-txt-primary animate-pulse" />
                                    )}
                                </div>
                                <span className={`
                                    text-[12px] font-medium mt-2.5 transition-colors
                                    ${isActive ? 'text-txt-primary' : isDone ? 'text-txt-secondary' : 'text-txt-faint'}
                                `}>
                                    {config.label}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Progress bar */}
            {currentState === 'executing' && progress > 0 && (
                <div className="mt-4 bg-surface-2 border border-edge rounded-xl p-4">
                    <div className="flex justify-between mb-2">
                        <span className="text-[13px] text-txt-secondary">Progress</span>
                        <span className="text-[13px] text-txt-primary font-mono font-medium">{progress}%</span>
                    </div>
                    <div className="h-1.5 bg-edge rounded-full overflow-hidden">
                        <div
                            className="h-full bg-txt-primary rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Failed */}
            {isFailed && (
                <div className="mt-4 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
                    <p className="text-[14px] text-red-400">
                        Task failed — check the logs panel for details.
                    </p>
                </div>
            )}
        </div>
    );
}
