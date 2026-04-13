/**
 * Hero Section
 * 
 * Premium landing page hero with gradient text and animated CTAs.
 */

'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui';

export default function Hero() {
    return (
        <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
            {/* Gradient background */}
            <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />

            {/* Subtle grid pattern */}
            <div className="absolute inset-0 opacity-[0.02]">
                <div className="absolute inset-0" style={{
                    backgroundImage: `linear-gradient(rgba(6, 182, 212, 0.1) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(6, 182, 212, 0.1) 1px, transparent 1px)`,
                    backgroundSize: '50px 50px'
                }} />
            </div>

            <div className="relative max-w-5xl mx-auto px-6 text-center">
                {/* Logo/Icon */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="mb-8"
                >
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 mb-6">
                        <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                    </div>
                </motion.div>

                {/* Heading */}
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6 bg-gradient-to-r from-slate-50 via-slate-200 to-slate-400 bg-clip-text text-transparent"
                >
                    Sentinel
                </motion.h1>

                {/* Subtitle */}
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="text-xl md:text-2xl text-slate-300 mb-4 max-w-3xl mx-auto"
                >
                    AI-powered file organization.{' '}
                    <span className="text-primary font-medium">Local-first.</span>{' '}
                    <span className="text-primary font-medium">Safe.</span>
                </motion.p>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="text-slate-400 mb-12 max-w-2xl mx-auto"
                >
                    Clean and organize your Downloads, Desktop, and Documents with AI—without files ever leaving your machine.
                </motion.p>

                {/* CTAs */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="flex flex-col sm:flex-row gap-4 justify-center items-center"
                >
                    <Button variant="primary" size="lg" className="min-w-[200px]">
                        Get Started
                    </Button>
                    <Button variant="secondary" size="lg" className="min-w-[200px]">
                        View Demo
                    </Button>
                </motion.div>

                {/* Quick install hint */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.6 }}
                    className="mt-16 inline-flex items-center gap-3 px-4 py-2 rounded-lg bg-slate-900/50 border border-slate-800"
                >
                    <code className="text-sm font-mono text-slate-300">
                        $ pip install sentinel-ai
                    </code>
                </motion.div>
            </div>
        </section>
    );
}
