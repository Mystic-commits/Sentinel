'use client';

import { useState } from 'react';
import { TASK_MODES, TaskMode } from '@/lib/types/task';
import { useStore } from '@/hooks/useStore';
import { api } from '@/lib/api/client';

export default function TaskComposer() {
    const [description, setDescription] = useState('');
    const [selectedMode, setSelectedMode] = useState<TaskMode>('file_organization');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { addTask } = useStore();

    const handleSubmit = async () => {
        if (!description.trim()) return;
        setIsSubmitting(true);

        try {
            const response = await api.createPlan(null, selectedMode, description) as any;
            const taskId = response.task_id;
            const now = new Date().toISOString();

            addTask({
                id: taskId,
                description,
                mode: selectedMode,
                state: 'planning',
                created_at: now,
                updated_at: now,
                logs: [{
                    id: crypto.randomUUID(),
                    message: 'Task started',
                    timestamp: now,
                    level: 'info',
                }],
            });

            setDescription('');
        } catch (error) {
            console.error('Failed to create task:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="px-8 py-6 max-w-3xl mx-auto w-full">
            {/* Input area */}
            <div className="bg-surface-2 border border-edge rounded-xl p-4 hover:border-edge-hover transition-colors">
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="What should Sentinel organize?"
                    rows={2}
                    className="
                        w-full bg-transparent border-0
                        text-[15px] text-txt-primary placeholder:text-txt-faint
                        focus:outline-none resize-none leading-relaxed
                    "
                />

                {/* Bottom bar */}
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-edge/50">
                    {/* Mode pills */}
                    <div className="flex items-center gap-1.5">
                        {TASK_MODES.map((mode) => (
                            <button
                                key={mode.id}
                                onClick={() => setSelectedMode(mode.id)}
                                className={`
                                    px-3 py-1.5 rounded-lg text-[13px] font-medium transition-all duration-150
                                    ${selectedMode === mode.id
                                        ? 'bg-white text-black'
                                        : 'text-txt-muted hover:text-txt-secondary hover:bg-surface-3'
                                    }
                                `}
                            >
                                {mode.label}
                            </button>
                        ))}
                    </div>

                    {/* Submit */}
                    <button
                        onClick={handleSubmit}
                        disabled={!description.trim() || isSubmitting}
                        className="
                            h-9 px-5 rounded-lg text-[13px] font-semibold
                            bg-white text-black
                            hover:bg-neutral-200
                            disabled:opacity-30 disabled:cursor-not-allowed
                            transition-all duration-150
                        "
                    >
                        {isSubmitting ? 'Starting...' : 'Run'}
                    </button>
                </div>
            </div>
        </div>
    );
}
