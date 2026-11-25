'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui';
import Link from 'next/link';

export default function Hero() {
    return (
        <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-32 pb-20">
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
                    Review proposed changes before applying them.
                </motion.p>

                {/* CTAs */}
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 }}
                    className="flex flex-col sm:flex-row gap-3 justify-center items-center"
                >
                    <Link href="/download">
                        <Button variant="primary" size="lg">
                            Download Now
                            <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                            </svg>
                        </Button>
                    </Link>
                    <Link href="https://github.com/Mystic-commits/Sentinel">
                        <Button variant="secondary" size="lg">View on GitHub</Button>
                    </Link>
                </motion.div>

            </div>
        </section>
    );
}
