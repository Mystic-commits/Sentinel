'use client';

import { motion } from 'framer-motion';

const docs = [
    {
        title: 'Getting Started',
        description: 'Quick setup guide to install Sentinel and organize your first folder in minutes.',
        href: 'https://github.com/Mystic-commits/Sentinel#-usage',
        icon: (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
            </svg>
        ),
    },
    {
        title: 'CLI Reference',
        description: 'Complete guide to all Sentinel commands, flags, and configuration options.',
        href: 'https://github.com/Mystic-commits/Sentinel#-usage',
        icon: (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m6.75 7.5 3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z" />
            </svg>
        ),
    },
    {
        title: 'API Reference',
        description: 'FastAPI endpoint documentation for integrating Sentinel into your workflow.',
        href: '/docs',
        icon: (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
            </svg>
        ),
    },
    {
        title: 'Architecture',
        description: 'Deep dive into Sentinel\'s system design, safety layers, and extension points.',
        href: 'https://github.com/Mystic-commits/Sentinel#%EF%B8%8F-tech-stack',
        icon: (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 7.125C2.25 6.504 2.754 6 3.375 6h6c.621 0 1.125.504 1.125 1.125v3.75c0 .621-.504 1.125-1.125 1.125h-6a1.125 1.125 0 01-1.125-1.125v-3.75zM14.25 8.625c0-.621.504-1.125 1.125-1.125h5.25c.621 0 1.125.504 1.125 1.125v8.25c0 .621-.504 1.125-1.125 1.125h-5.25a1.125 1.125 0 01-1.125-1.125v-8.25zM3.75 16.125c0-.621.504-1.125 1.125-1.125h5.25c.621 0 1.125.504 1.125 1.125v2.25c0 .621-.504 1.125-1.125 1.125h-5.25a1.125 1.125 0 01-1.125-1.125v-2.25z" />
            </svg>
        ),
    },
    {
        title: 'Safety & Privacy',
        description: 'How Sentinel protects your data with multi-layer safety guarantees.',
        href: 'https://github.com/Mystic-commits/Sentinel#-safety-guarantees',
        icon: (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
        ),
    },
    {
        title: 'Contributing',
        description: 'Guidelines for contributing code, reporting bugs, and improving docs.',
        href: 'https://github.com/Mystic-commits/Sentinel#-contributing',
        icon: (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
            </svg>
        ),
    },
];

export default function DocsSection() {
    return (
        <section id="docs" className="py-24 px-6 bg-surface-1 relative">
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
                        Documentation
                    </h2>
                    <p className="text-[16px] text-txt-secondary max-w-xl mx-auto leading-relaxed">
                        Everything you need to get started, integrate, and contribute.
                    </p>
                </motion.div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {docs.map((doc, index) => (
                        <motion.a
                            key={doc.title}
                            href={doc.href}
                            target={doc.href.startsWith('http') ? '_blank' : undefined}
                            rel={doc.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                            initial={{ opacity: 0, y: 12 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.3, delay: index * 0.06 }}
                            className="bg-surface-0 border border-edge rounded-xl p-6 hover:border-edge-hover hover:bg-surface-0/80 transition-all duration-200 group block"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-10 h-10 rounded-lg bg-surface-2 border border-edge flex items-center justify-center text-txt-muted group-hover:text-txt-primary group-hover:border-edge-hover transition-all duration-200">
                                    {doc.icon}
                                </div>
                                <svg
                                    className="w-4 h-4 text-txt-faint group-hover:text-txt-secondary group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all duration-200"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    strokeWidth={2}
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
                                </svg>
                            </div>
                            <h3 className="text-[16px] font-semibold text-txt-primary mb-2 group-hover:text-white transition-colors">
                                {doc.title}
                            </h3>
                            <p className="text-[14px] text-txt-secondary leading-relaxed">
                                {doc.description}
                            </p>
                        </motion.a>
                    ))}
                </div>
            </div>
        </section>
    );
}
