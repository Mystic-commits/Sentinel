'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function ConnectCTA() {
    return (
        <section className="pt-24 pb-32 px-6 relative overflow-hidden">
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-surface-0/50 pointer-events-none" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />

            <div className="relative max-w-4xl mx-auto text-center">
                <motion.h2
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-4xl md:text-5xl font-bold text-txt-primary mb-6 tracking-tight"
                >
                    Ready to reclaim your digital space?
                </motion.h2>
                <motion.p
                    initial={{ opacity: 0, y: 12 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                    className="text-lg text-txt-secondary mb-10 max-w-xl mx-auto"
                >
                    Join thousands of users organizing their lives with Sentinel’s local-first AI.
                </motion.p>
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="flex items-center justify-center gap-4"
                >
                    <Link
                        href="/download"
                        className="px-8 py-4 bg-white text-black font-bold rounded-xl hover:bg-neutral-200 transition-all hover:scale-105 shadow-lg shadow-white/10"
                    >
                        Download for Free
                    </Link>
                    <Link
                        href="/how-it-works"
                        className="px-8 py-4 bg-surface-2 text-txt-primary font-semibold rounded-xl hover:bg-surface-3 transition-colors border border-edge"
                    >
                        See Demo
                    </Link>
                </motion.div>
            </div>
        </section>
    );
}
