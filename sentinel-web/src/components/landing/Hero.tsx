'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowDown, ArrowRight, FileText, FolderOpen, Image, RotateCcw } from 'lucide-react';

const sample = [
    { name: 'invoice-may.pdf', folder: 'Documents', icon: FileText },
    { name: 'lake-weekend.jpg', folder: 'Photos', icon: Image },
    { name: 'notes.txt', folder: 'Notes', icon: FileText },
];

export default function Hero() {
    const [selected, setSelected] = useState([true, true, false]);
    const [applied, setApplied] = useState(false);
    const count = selected.filter(Boolean).length;

    return (
        <section className="bg-[#0b1312] px-5 pb-16 pt-28 sm:pt-32">
            <div className="mx-auto max-w-5xl">
                <h1 className="max-w-3xl font-serif text-5xl font-semibold leading-[1.02] tracking-[-0.065em] text-[#f3f6ed] sm:text-7xl">
                    A tidier folder.<br /> <span className="text-[#a6edc3]">Your call.</span>
                </h1>
                <p className="mt-5 max-w-xl text-base leading-relaxed text-[#beccc4] sm:text-lg">
                    Sentinel is a local AI file organizer. Review where each file would go,
                    choose what moves, and undo eligible changes from your history.
                </p>
                <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3">
                    <a href="#sample-folder" className="inline-flex items-center gap-2 rounded-lg bg-[#a6edc3] px-4 py-3 font-semibold text-[#12241c]">
                        Try the sample <ArrowDown size={16} aria-hidden />
                    </a>
                    <Link href="/download" className="text-sm font-medium text-[#d2ded5] underline underline-offset-4">
                        Developer preview
                    </Link>
                </div>

                <section id="sample-folder" aria-labelledby="sample-title" className="mt-10 scroll-mt-24 overflow-hidden rounded-2xl border border-[#34483d] bg-[#101c18]">
                    <header className="flex items-center gap-3 px-4 py-4 sm:px-6">
                        <FolderOpen size={20} className="text-[#a6edc3]" aria-hidden />
                        <h2 id="sample-title" className="font-semibold">Sample Downloads</h2>
                    </header>
                    <ul className="divide-y divide-[#293b33]">
                        {sample.map(({ name, folder, icon: Icon }, index) => (
                            <li key={name}>
                                <label className="grid grid-cols-[auto_minmax(0,1fr)] items-center gap-x-3 gap-y-1 px-4 py-3 text-sm sm:grid-cols-[auto_minmax(0,1fr)_minmax(0,1fr)] sm:px-6">
                                    <input type="checkbox" checked={selected[index]} disabled={applied}
                                        aria-label={`Move ${name}`}
                                        onChange={event => setSelected(selected.map((value, i) => i === index ? event.target.checked : value))}
                                        className="size-4 accent-[#a6edc3]" />
                                    <span className="flex min-w-0 items-center gap-2 font-mono text-[#edf6ef]">
                                        <Icon size={16} className="shrink-0 text-[#9cafa3]" aria-hidden />
                                        <span className="break-all">{name}</span>
                                    </span>
                                    <span className="col-start-2 flex items-center gap-2 text-[#b2c3b8] sm:col-start-auto">
                                        <ArrowRight size={14} aria-hidden />
                                        {selected[index] ? `${folder}/` : 'Keep in Downloads'}
                                    </span>
                                </label>
                            </li>
                        ))}
                    </ul>
                    <footer className="flex flex-wrap items-center justify-between gap-3 bg-[#15251e] px-4 py-4 sm:px-6">
                        <p role="status" className="text-sm text-[#c8d8cf]">
                            {applied ? `Moved ${count} sample ${count === 1 ? 'file' : 'files'}.` : `${count} selected · sample files only`}
                        </p>
                        <button type="button" disabled={count === 0}
                            onClick={() => setApplied(!applied)}
                            className="inline-flex items-center gap-2 rounded-md border border-[#71917d] px-3 py-2 text-sm font-semibold text-[#d5f5df] disabled:opacity-50">
                            {applied && <RotateCcw size={15} aria-hidden />}
                            {applied ? 'Undo sample moves' : `Apply ${count} ${count === 1 ? 'move' : 'moves'}`}
                        </button>
                    </footer>
                </section>
            </div>
        </section>
    );
}
