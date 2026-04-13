/**
 * Timeline Component
 * 
 * Clean status indicator for task progression.
 */

'use client';

import { STATE_CONFIG, TaskState } from '@/lib/types/task';

const TIMELINE_STATES: TaskState[] = [
    'idle',
    'scanning',
    'planning',
    'review',
    'executing',
    'completed',
];

interface TimelineProps {
    currentState: TaskState;
    progress?: number;
}

export default function Timeline({ currentState, progress = 0 }: TimelineProps) {
    const currentIndex = TIMELINE_STATES.indexOf(currentState);

    return (
        <div className="p-6 bg-[#141414] border border-[#1f1f1f] rounded-xl">
            <h3 className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-6">
                Status
            </h3>

            {/* Steps */}
            <div className="relative">
                {/* Progress line */}
                <div className="absolute top-4 left-0 right-0 h-px bg-[#1f1f1f]">
                    <div
                        className="h-full bg-blue-500 transition-all duration-500"
                        style={{ width: `${(currentIndex / (TIMELINE_STATES.length - 1)) * 100}%` }}
                    />
                </div>

                {/* State dots */}
                <div className="relative flex justify-between">
                    {TIMELINE_STATES.map((state, index) => {
                        const config = STATE_CONFIG[state];
                        const isActive = index === currentIndex;
                        const isCompleted = index < currentIndex;
                        const isFailed = currentState === 'failed' && state === currentState;

                        return (
                            <div key={state} className="flex flex-col items-center">
                                <div
                                    className={`
                                        w-8 h-8 rounded-full border flex items-center justify-center text-xs relative z-10 transition-colors duration-200
                                        ${isActive
                                            ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                                            : isCompleted
                                                ? 'border-blue-500 bg-blue-500 text-white'
                                                : isFailed
                                                    ? 'border-red-500 bg-red-500/10 text-red-400'
                                                    : 'border-[#2a2a2a] bg-[#0a0a0a] text-neutral-600'
                                        }
                                    `}
                                >
                                    {config.icon}
                                </div>

                                <span className={`
                                    text-[10px] font-medium uppercase tracking-wider mt-2 transition-colors
                                    ${isActive ? 'text-blue-400' : isCompleted ? 'text-neutral-400' : 'text-neutral-600'}
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
                <div className="mt-6">
                    <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[10px] uppercase text-neutral-500 tracking-wider">
                            Progress
                        </span>
                        <span className="text-xs text-neutral-400 font-mono">{progress}%</span>
                    </div>
                    <div className="h-1 bg-[#1f1f1f] rounded-full overflow-hidden">
                        <div
                            className="h-full bg-blue-500 transition-all duration-300 rounded-full"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}
