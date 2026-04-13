/**
 * Feature Grid
 * 
 * 2x2 grid showcasing key features with hover effects.
 */

'use client';

import { motion } from 'framer-motion';
import { Card } from '@/components/ui';

const features = [
    {
        icon: '🔒',
        title: 'Local-First',
        description: 'All processing happens on your machine. Your files never leave your computer. Complete privacy guaranteed.',
    },
    {
        icon: '🗑️',
        title: 'Safe Deletes',
        description: 'Files go to trash, never permanently deleted. Every operation is reversible and safe.',
    },
    {
        icon: '⏪',
        title: 'Undo Anything',
        description: 'Every operation is logged and undoable. Restore any change with a single command.',
    },
    {
        icon: '📋',
        title: 'Task History',
        description: 'Complete audit trail of all changes. Track what was organized, when, and where.',
    },
];

export default function FeatureGrid() {
    return (
        <section className="py-24 px-6 bg-background-elevated">
            <div className="max-w-6xl mx-auto">
                {/* Section header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl md:text-5xl font-bold text-slate-50 mb-4">
                        Built for Safety & Control
                    </h2>
                    <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                        Sentinel puts you in control with safety-first design and complete transparency.
                    </p>
                </motion.div>

                {/* Feature grid */}
                <div className="grid md:grid-cols-2 gap-6">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                        >
                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                transition={{ duration: 0.2 }}
                            >
                                <Card variant="interactive" className="h-full">
                                    <div className="text-5xl mb-4">{feature.icon}</div>
                                    <h3 className="text-xl font-semibold text-slate-50 mb-3">
                                        {feature.title}
                                    </h3>
                                    <p className="text-slate-400 leading-relaxed">
                                        {feature.description}
                                    </p>
                                </Card>
                            </motion.div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
