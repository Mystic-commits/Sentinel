'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

const platforms = [
    {
        name: 'macOS',
        description: 'Native desktop app built with Tauri. Lightweight and fast.',
        fileName: 'Sentinel_0.1.0_x64.dmg',
        downloadUrl: '/downloads/Sentinel_0.1.0_x64.dmg',
        buttonLabel: 'Download .dmg',
        icon: (
            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
            </svg>
        ),
    },
    {
        name: 'Windows',
        description: 'Native installer for Windows 10+. No dependencies needed.',
        fileName: 'Sentinel_0.1.0_x64.msi',
        downloadUrl: '/downloads/Sentinel_0.1.0_x64.msi',
        buttonLabel: 'Download .msi',
        icon: (
            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 12V6.75l6-1.32v6.48L3 12zm17-9v8.75l-10 .15V5.21L20 3zM3 13l6 .09v6.81l-6-1.15V13zm7 .25l10 .15V21l-10-1.91V13.25z" />
            </svg>
        ),
    },
    {
        name: 'Linux / CLI',
        description: 'Install via pip. Works on any platform with Python 3.11+.',
        fileName: null,
        downloadUrl: null,
        buttonLabel: 'Copy command',
        installCommand: 'pip install sentinel-ai',
        icon: (
            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m6.75 7.5 3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0 0 21 18V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v12a2.25 2.25 0 0 0 2.25 2.25z" />
            </svg>
        ),
    },
];

export default function DownloadSection() {
    const [copied, setCopied] = useState(false);

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <section id="download" className="py-24 px-6 relative">
            {/* Gradient divider */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-px bg-gradient-to-r from-transparent via-edge to-transparent" />

            <div className="max-w-5xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 14 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.35 }}
                    className="text-center mb-14"
                >
                    <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold text-txt-primary tracking-tight mb-4">
                        Download Sentinel
                    </h2>
                    <p className="text-[16px] text-txt-secondary max-w-xl mx-auto leading-relaxed">
                        Choose your platform. Desktop app or command line — same powerful engine.
                    </p>
                </motion.div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {platforms.map((platform, index) => (
                        <motion.div
                            key={platform.name}
                            initial={{ opacity: 0, y: 12 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.3, delay: index * 0.08 }}
                        >
                            <div className="bg-surface-1 border border-edge rounded-xl p-6 h-full hover:border-edge-hover transition-all duration-200 group flex flex-col">
                                <div className="w-14 h-14 rounded-xl bg-surface-2 border border-edge flex items-center justify-center text-txt-muted group-hover:text-txt-primary group-hover:border-edge-hover transition-all duration-200 mb-5">
                                    {platform.icon}
                                </div>
                                <h3 className="text-[18px] font-semibold text-txt-primary mb-2">
                                    {platform.name}
                                </h3>
                                <p className="text-[14px] text-txt-secondary leading-relaxed mb-6 flex-1">
                                    {platform.description}
                                </p>

                                {platform.installCommand ? (
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-surface-0 border border-edge font-mono text-[13px] text-txt-secondary">
                                            <span className="text-emerald-400">❯</span>
                                            <span className="flex-1 truncate">{platform.installCommand}</span>
                                        </div>
                                        <button
                                            onClick={() => handleCopy(platform.installCommand!)}
                                            className="w-full h-10 px-4 text-[14px] font-semibold bg-surface-2 text-txt-primary border border-edge rounded-lg hover:bg-surface-3 hover:border-edge-hover transition-colors flex items-center justify-center gap-2"
                                        >
                                            {copied ? (
                                                <>
                                                    <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                                    </svg>
                                                    Copied!
                                                </>
                                            ) : (
                                                <>
                                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 7.5V6.108c0-1.135.845-2.098 1.976-2.192.373-.03.748-.057 1.123-.08M15.75 18H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08M15.75 18.75v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5A3.375 3.375 0 006.375 7.5H6" />
                                                    </svg>
                                                    {platform.buttonLabel}
                                                </>
                                            )}
                                        </button>
                                    </div>
                                ) : (
                                    <a
                                        href={platform.downloadUrl!}
                                        download
                                        className="w-full h-10 px-4 text-[14px] font-semibold bg-white text-black rounded-lg hover:bg-neutral-200 transition-colors flex items-center justify-center gap-2"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                        </svg>
                                        {platform.buttonLabel}
                                    </a>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </div>

                <motion.p
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.35, delay: 0.3 }}
                    className="text-[13px] text-txt-muted text-center mt-8"
                >
                    Requires Python 3.11+ for CLI · Ollama for AI features ·{' '}
                    <a
                        href="https://github.com/Mystic-commits/Sentinel/releases"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-txt-secondary hover:text-txt-primary transition-colors underline underline-offset-2"
                    >
                        All releases →
                    </a>
                </motion.p>
            </div>
        </section>
    );
}
