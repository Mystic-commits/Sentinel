'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

const steps = [
    { label: 'Install', code: 'pip install sentinel-ai' },
    { label: 'Scan', code: 'sentinel scan ~/Downloads' },
    { label: 'Plan', code: 'sentinel plan ~/Downloads --mode organize' },
    { label: 'Execute', code: 'sentinel apply task-abc-123' },
];

export default function InstallSection() {
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

    const copyToClipboard = (text: string, index: number) => {
        navigator.clipboard.writeText(text);
        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    return (
        <section className="py-24 px-6 bg-surface-1 relative">
            {/* Gradient divider */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-px bg-gradient-to-r from-transparent via-edge to-transparent" />

            <div className="max-w-3xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 14 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.35 }}
                    className="text-center mb-14"
                >
                    <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold text-txt-primary tracking-tight mb-4">
                        Get started in seconds
                    </h2>
                    <p className="text-[16px] text-txt-secondary max-w-xl mx-auto leading-relaxed">
                        Four commands to go from chaos to organized.
                    </p>
                </motion.div>

                <div className="space-y-3">
                    {steps.map((step, index) => (
                        <motion.div
                            key={step.label}
                            initial={{ opacity: 0, y: 10 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.3, delay: index * 0.06 }}
                        >
                            <div className="bg-surface-0 border border-edge rounded-xl overflow-hidden hover:border-edge-hover transition-colors group">
                                <div className="flex items-center justify-between px-4 py-2.5 border-b border-edge">
                                    <div className="flex items-center gap-2.5">
                                        <span className="w-5 h-5 rounded-full bg-surface-2 border border-edge flex items-center justify-center text-[11px] font-mono text-txt-muted group-hover:border-edge-hover transition-colors">
                                            {index + 1}
                                        </span>
                                        <span className="text-[13px] font-medium text-txt-secondary">
                                            {step.label}
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => copyToClipboard(step.code, index)}
                                        className="text-[12px] px-2.5 py-1 rounded-lg text-txt-faint hover:text-txt-secondary hover:bg-surface-2 transition-colors"
                                    >
                                        {copiedIndex === index ? '✓ Copied' : 'Copy'}
                                    </button>
                                </div>
                                <div className="px-4 py-3 font-mono text-[14px] text-txt-primary">
                                    <span className="text-emerald-400 mr-2">❯</span>
                                    {step.code}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.35, delay: 0.3 }}
                    className="mt-10 text-center"
                >
                    <p className="text-[13px] text-txt-muted mb-4">
                        Requires Python 3.11+ · Ollama for AI features
                    </p>
                    <a
                        href="https://github.com/yourusername/sentinel"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-[14px] text-txt-secondary hover:text-txt-primary transition-colors"
                    >
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                        </svg>
                        View on GitHub
                    </a>
                </motion.div>
            </div>
        </section>
    );
}
