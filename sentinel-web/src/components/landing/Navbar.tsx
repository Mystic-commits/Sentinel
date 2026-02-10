'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';

const navLinks = [
    { label: 'Features', href: '#features' },
    { label: 'How It Works', href: '#demo' },
    { label: 'Download', href: '#download' },
    { label: 'Docs', href: '#docs' },
];

export default function Navbar() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <motion.nav
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className={`
                fixed top-0 left-0 right-0 z-50 transition-all duration-300
                ${scrolled
                    ? 'bg-surface-0/80 backdrop-blur-xl border-b border-edge/60 shadow-sm'
                    : 'bg-transparent border-b border-transparent'
                }
            `}
        >
            <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between relative">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2.5 group shrink-0">
                    <div className="w-9 h-9 flex items-center justify-center text-emerald-400">
                        {/* Shield + Eye Logo */}
                        <svg viewBox="0 0 24 24" fill="none" className="w-full h-full" stroke="currentColor" strokeWidth={1.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
                        </svg>
                    </div>
                    <span className="text-[18px] font-bold text-txt-primary tracking-tight group-hover:text-white transition-colors">
                        Sentinel
                    </span>
                </Link>

                {/* Center Nav Links - Absolute Centering */}
                <div className="hidden md:flex items-center gap-8 absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                    {navLinks.map((link) => (
                        <a
                            key={link.label}
                            href={link.href}
                            className="text-[15px] font-medium text-txt-muted hover:text-txt-primary transition-colors py-1"
                        >
                            {link.label}
                        </a>
                    ))}
                </div>

                {/* Right actions */}
                <div className="flex items-center gap-4 shrink-0">
                    <a
                        href="https://github.com/Mystic-commits/Sentinel"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hidden sm:flex items-center gap-2 text-[14px] text-txt-muted hover:text-txt-primary transition-colors"
                    >
                        GitHub
                    </a>
                    <Link
                        href="/dashboard"
                        className="
                            h-10 px-5 text-[14px] font-semibold bg-white text-black rounded-xl
                            flex items-center shadow-[0_0_20px_rgba(255,255,255,0.1)]
                            hover:bg-neutral-200 hover:shadow-[0_0_25px_rgba(255,255,255,0.2)]
                            hover:-translate-y-0.5
                            transition-all duration-200
                        "
                    >
                        Open Dashboard
                    </Link>
                </div>
            </div>
        </motion.nav>
    );
}
