'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ── Constants ─────────────────────────────────────────────────────────────────
// Magic numbers pulled into a named constant so the intent is obvious
const CYCLE_INTERVAL_MS = 2800;

type TaskState = 'SCANNING' | 'PLANNING' | 'REVIEW' | 'EXECUTING' | 'COMPLETE';

const states: TaskState[] = ['SCANNING', 'PLANNING', 'REVIEW', 'EXECUTING', 'COMPLETE'];

const stateContent: Record<TaskState, { label: string; title: string; lines: string[] }> = {
    SCANNING: {
        label: 'Scan',
        title: 'sentinel scan ~/Downloads',
        lines: [
            'Found 247 files (1.2 GB)',
            'Analyzing file types...',
            'Detecting duplicates...',
            '83 images, 42 documents, 31 archives',
        ],
    },
    PLANNING: {
        label: 'Plan',
        title: 'sentinel plan ~/Downloads --strategy file_types',
        lines: [
            'Categorizing by file type',
            'Grouping by creation date',
            'Creating folder structure',
            'Plan: 5 folders, 142 moves',
        ],
    },
    REVIEW: {
        label: 'Review',
        title: 'Plan ready for review',
        lines: [
            '142 files to organize',
            '5 new folders to create',
            '3 ambiguous items flagged',
            'Waiting for approval...',
        ],
    },
    EXECUTING: {
        label: 'Execute',
        title: 'sentinel apply task-abc-123 --actions 1,2',
        lines: [
            'Created Images/',
            'Moved photo_001.jpg → Images/',
            'Created Documents/2024/',
            'Progress: 127/142 files',
        ],
    },
    COMPLETE: {
        label: 'Done',
        title: 'Task complete',
        lines: [
            '142 files organized',
            '5 folders created',
            '0 errors encountered',
            'All operations logged (undoable)',
        ],
    },
};

// ── Sub-component: the small circle/dot indicator beside each pipeline step ───
// Extracted so the parent list doesn't have nested conditional JSX everywhere
function StateIndicator({ isActive, isDone }: { isActive: boolean; isDone: boolean }) {
    return (
        <div className={`
            w-5 h-5 rounded-full flex items-center justify-center shrink-0 transition-all duration-200
            ${isDone
                ? 'bg-txt-primary text-black'
                : isActive
                    ? 'border-2 border-txt-primary'
                    : 'border border-edge'
            }
        `}>
            {isDone && (
                <svg className="w-2.5 h-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 13l4 4L19 7" />
                </svg>
            )}
            {isActive && (
                <div className="w-1.5 h-1.5 rounded-full bg-txt-primary animate-pulse" />
            )}
        </div>
    );
}

// ── Sub-component: a single animated line in the terminal output ──────────────
// Extracted so TerminalOutput stays clean and this piece is reusable
function TerminalLine({ text, index }: { text: string; index: number }) {
    return (
        <motion.p
            initial={{ opacity: 0, x: 6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.08 }}
            className="text-[13px] text-txt-secondary font-mono leading-relaxed flex items-start gap-2"
        >
            <span className="text-txt-faint shrink-0">→</span>
            <span>{text}</span>
        </motion.p>
    );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function AnimatedDemo() {
    const [currentStateIndex, setCurrentStateIndex] = useState(0);

    const currentState = states[currentStateIndex];
    const content = stateContent[currentState];

    // Derived value: what % of the pipeline is done (used for the progress bar)
    const progressPercent = ((currentStateIndex + 1) / states.length) * 100;

    useEffect(() => {
        const interval = setInterval(() => {
            // Loop back to 0 when we reach the end
            setCurrentStateIndex((prev) => (prev + 1) % states.length);
        }, CYCLE_INTERVAL_MS);

        // Cleanup: clear the timer when the component unmounts
        return () => clearInterval(interval);
    }, []);

    return (
        <section id="demo" className="py-24 px-6 relative">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-px bg-gradient-to-r from-transparent via-edge to-transparent" />

            <div className="max-w-5xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.35 }}
                    className="text-center mb-14"
                >
                    <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold text-txt-primary tracking-tight mb-4">
                        See it in action
                    </h2>
                    <p className="text-[16px] text-txt-secondary max-w-xl mx-auto leading-relaxed">
                        Sentinel guides your files through a transparent, multi-stage pipeline.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: 0.1 }}
                >
                    <div className="grid md:grid-cols-[1fr_1.2fr] gap-4">

                        {/* ── Pipeline state list ── */}
                        <div className="bg-surface-1 border border-edge rounded-xl p-5 space-y-1.5">
                            <p className="text-[11px] font-semibold text-txt-faint uppercase tracking-[0.12em] mb-3">
                                Pipeline
                            </p>
                            {states.map((state, index) => {
                                const isActive = state === currentState;
                                const isDone = index < currentStateIndex;
                                return (
                                    <motion.div
                                        key={state}
                                        animate={{ backgroundColor: isActive ? 'rgba(255,255,255,0.04)' : 'transparent' }}
                                        transition={{ duration: 0.2 }}
                                        className={`
                                            flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                                            ${isActive ? 'border border-edge' : 'border border-transparent'}
                                        `}
                                    >
                                        {/* Extracted into its own component — keeps this list readable */}
                                        <StateIndicator isActive={isActive} isDone={isDone} />
                                        <span className={`
                                            text-[14px] font-medium transition-colors duration-200
                                            ${isActive ? 'text-txt-primary' : isDone ? 'text-txt-secondary' : 'text-txt-muted'}
                                        `}>
                                            {stateContent[state].label}
                                        </span>
                                    </motion.div>
                                );
                            })}
                        </div>

                        {/* ── Terminal output panel ── */}
                        <div className="bg-surface-1 border border-edge rounded-xl overflow-hidden">
                            <div className="flex items-center gap-2 px-4 py-3 border-b border-edge">
                                <div className="flex gap-1.5">
                                    <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
                                    <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
                                    <div className="w-3 h-3 rounded-full bg-[#28c840]" />
                                </div>
                                <span className="text-[12px] text-txt-faint font-mono ml-2">sentinel — zsh</span>
                            </div>

                            <div className="p-5 min-h-[220px]">
                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={currentState}
                                        initial={{ opacity: 0, y: 6 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -6 }}
                                        transition={{ duration: 0.18 }}
                                    >
                                        <p className="text-[14px] text-txt-primary font-medium font-mono mb-4">
                                            <span className="text-emerald-400">❯</span> {content.title.toLowerCase()}
                                        </p>
                                        <div className="space-y-2">
                                            {/* Each line extracted into TerminalLine — clean loop */}
                                            {content.lines.map((line, i) => (
                                                <TerminalLine key={i} text={line} index={i} />
                                            ))}
                                        </div>
                                    </motion.div>
                                </AnimatePresence>
                            </div>

                            {/* Progress bar */}
                            <div className="px-5 pb-4">
                                <div className="h-1 bg-edge rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-white/60 to-white rounded-full"
                                        initial={{ width: '0%' }}
                                        animate={{ width: `${progressPercent}%` }}
                                        transition={{ duration: 0.4 }}
                                    />
                                </div>
                            </div>
                        </div>

                    </div>
                </motion.div>
            </div>
        </section>
    );
}