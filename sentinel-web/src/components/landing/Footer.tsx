import Link from 'next/link';

const footerSections = [
    {
        title: 'Product',
        links: [
            { label: 'Dashboard', href: '/dashboard' },
            { label: 'Downloads', href: '#download' },
            { label: 'Changelog', href: 'https://github.com/Mystic-commits/Sentinel/releases', external: true },
        ],
    },
    {
        title: 'Resources',
        links: [
            { label: 'Documentation', href: '#docs' },
            { label: 'API Reference', href: 'http://localhost:8000/docs', external: true },
            { label: 'GitHub', href: 'https://github.com/Mystic-commits/Sentinel', external: true },
        ],
    },
    {
        title: 'Community',
        links: [
            { label: 'Discussions', href: 'https://github.com/Mystic-commits/Sentinel/discussions', external: true },
            { label: 'Issues', href: 'https://github.com/Mystic-commits/Sentinel/issues', external: true },
            { label: 'Contributing', href: 'https://github.com/Mystic-commits/Sentinel#-contributing', external: true },
        ],
    },
];

export default function Footer() {
    return (
        <footer className="py-16 px-6 border-t border-edge">
            <div className="max-w-5xl mx-auto">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-12">
                    {/* Brand */}
                    <div className="col-span-2 md:col-span-1">
                        <Link href="/" className="flex items-center gap-2.5 mb-4">
                            <div className="w-7 h-7 rounded-lg bg-white flex items-center justify-center">
                                <span className="text-[12px] font-bold text-black">S</span>
                            </div>
                            <span className="text-[15px] font-semibold text-txt-primary">Sentinel</span>
                        </Link>
                        <p className="text-[13px] text-txt-muted leading-relaxed max-w-[200px]">
                            AI-powered file organization that runs entirely on your machine.
                        </p>
                    </div>

                    {/* Link columns */}
                    {footerSections.map((section) => (
                        <div key={section.title}>
                            <h4 className="text-[13px] font-semibold text-txt-secondary uppercase tracking-[0.08em] mb-4">
                                {section.title}
                            </h4>
                            <ul className="space-y-2.5">
                                {section.links.map((link) => (
                                    <li key={link.label}>
                                        {link.external ? (
                                            <a
                                                href={link.href}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-[14px] text-txt-muted hover:text-txt-primary transition-colors"
                                            >
                                                {link.label}
                                            </a>
                                        ) : (
                                            <Link
                                                href={link.href}
                                                className="text-[14px] text-txt-muted hover:text-txt-primary transition-colors"
                                            >
                                                {link.label}
                                            </Link>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="pt-8 border-t border-edge flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-[13px] text-txt-faint">
                        © {new Date().getFullYear()} Sentinel. Built with safety and privacy in mind.
                    </p>
                    <div className="flex items-center gap-4">
                        <a
                            href="https://github.com/Mystic-commits/Sentinel"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-txt-muted hover:text-txt-primary transition-colors"
                        >
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
