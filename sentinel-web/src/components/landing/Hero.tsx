'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui';
import Link from 'next/link';

export default function Hero() {
    return (
        <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
            {/* Background effects */}
            <div className="absolute inset-0">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(255,255,255,0.04)_0%,_transparent_50%)]" />
                {/* Subtle grid */}
                <div
                    className="absolute inset-0 opacity-[0.03]"
                    style={{
                        backgroundImage: `linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px)`,
                        backgroundSize: '64px 64px',
                    }}
                />
                {/* Glow orbs */}
                <div className="absolute top-[-20%] left-[20%] w-[500px] h-[500px] rounded-full bg-white/[0.015] blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[10%] w-[400px] h-[400px] rounded-full bg-white/[0.01] blur-[100px]" />
            </div>

            <div className="relative max-w-4xl mx-auto px-6 text-center">
                {/* Heading */}
                <motion.h1
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.08 }}
                    className="text-[clamp(3rem,8vw,5.5rem)] font-bold leading-[1.05] tracking-[-0.03em] text-txt-primary mb-6"
                >
                    Organize your files
                    <br />
                    <span className="bg-gradient-to-r from-white/60 via-white/40 to-white/20 bg-clip-text text-transparent">
                        with AI precision
                    </span>
                </motion.h1>

                {/* Subtitle */}
                <motion.p
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.14 }}
                    className="text-[18px] text-txt-secondary max-w-xl mx-auto mb-10 leading-relaxed"
                >
                    Sentinel scans, plans, and organizes your files using local AI.
                    Nothing ever leaves your machine.
                </motion.p>

                {/* CTAs */}
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 }}
                    className="flex flex-col sm:flex-row gap-3 justify-center items-center"
                >
                    <Link href="/dashboard">
                        <Button variant="primary" size="lg">
                            Open Dashboard
                            <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                            </svg>
                        </Button>
                    </Link>
                    <Button variant="secondary" size="lg">
                        View on GitHub
                    </Button>
                </motion.div>

                {/* Terminal snippet */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.4, delay: 0.3 }}
                    className="mt-16 inline-flex items-center gap-3 px-5 py-3 rounded-xl bg-surface-1 border border-edge group hover:border-edge-hover transition-colors"
                >
                    <span className="text-txt-faint font-mono text-[14px]">$</span>
                    <code className="text-[14px] font-mono text-txt-secondary">
                        pip install sentinel-ai
                    </code>
                    <button className="text-[12px] text-txt-faint hover:text-txt-secondary transition-colors px-2 py-1 rounded-lg hover:bg-surface-2">
                        Copy
                    </button>
                </motion.div>

                {/* Stats bar */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.4, delay: 0.38 }}
                    className="mt-12 flex items-center justify-center gap-8"
                >
                    {[
                        { value: '100%', label: 'Local' },
                        { value: '0', label: 'Data sent' },
                        { value: '∞', label: 'Undoable' },
                    ].map((stat) => (
                        <div key={stat.label} className="text-center">
                            <p className="text-[20px] font-semibold text-txt-primary tracking-tight">{stat.value}</p>
                            <p className="text-[12px] text-txt-faint">{stat.label}</p>
                        </div>
                    ))}
                </motion.div>
            </div>
        </section>
    );
}
