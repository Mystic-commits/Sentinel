'use client';

import { motion } from 'framer-motion';

const features = [
    {
        title: 'Privacy First',
        description: '100% local processing. Your data never leaves your device.',
        icon: (
            <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
            </svg>
        ),
        colSpan: 'md:col-span-1',
        bg: 'bg-gradient-to-br from-surface-2 to-surface-1',
    },
    {
        title: 'Intelligent Sorting',
        description: 'Automatically categorizes files by type, content, and context.',
        icon: (
            <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
            </svg>
        ),
        colSpan: 'md:col-span-2',
        bg: 'bg-gradient-to-br from-surface-2 to-[#0a0a0a]',
    },
    {
        title: 'Blazing Fast',
        description: 'Written in high-performance native code for instant results.',
        icon: (
            <svg className="w-6 h-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
        ),
        colSpan: 'md:col-span-3',
        bg: 'bg-gradient-to-r from-surface-1 via-surface-2 to-surface-1',
    },
];

export default function HomeBento() {
    return (
        <section className="py-20 px-6 relative">
            <div className="max-w-5xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {features.map((feature, i) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: i * 0.1 }}
                            className={`${feature.colSpan} relative group rounded-2xl border border-edge overflow-hidden hover:border-edge-hover transition-colors`}
                        >
                            <div className={`absolute inset-0 opacity-50 ${feature.bg}`} />
                            <div className="relative p-8 h-full flex flex-col justify-center">
                                <div className="mb-4 inline-flex items-center justify-center w-12 h-12 rounded-xl bg-surface-1 border border-edge shadow-sm">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-bold text-txt-primary mb-2">
                                    {feature.title}
                                </h3>
                                <p className="text-txt-secondary leading-relaxed">
                                    {feature.description}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
