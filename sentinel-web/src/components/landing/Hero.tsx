'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowDown, ArrowRight, Check, FileText, Image, RotateCcw } from 'lucide-react';
import SiteMark from './SiteMark';

const files = [
    { name: 'May invoice.pdf', folder: 'Documents', icon: FileText },
    { name: 'Coastline.jpg', folder: 'Photos', icon: Image },
    { name: 'Project notes.txt', folder: 'Notes', icon: FileText },
];

export default function Hero() {
    const [selected, setSelected] = useState([true, true, false]);
    const [applied, setApplied] = useState(false);
    const count = selected.filter(Boolean).length;

    return (
        <>
            <section className="site-shell site-intro">
                <h1>Find a place<br />for every file<span>.</span></h1>
                <div className="site-intro-side">
                    <p>Sentinel organizes files on your computer with local AI. Review every move before it happens, and restore eligible changes from your history.</p>
                    <div className="site-actions">
                        <a className="site-button" href="#sample-folder">Try the demo <ArrowDown size={16} aria-hidden /></a>
                        <Link className="site-text-link" href="/how-it-works">How it works <ArrowRight size={16} aria-hidden /></Link>
                    </div>
                </div>
            </section>

            <div className="site-shell">
                <section className="product-stage" id="sample-folder" aria-labelledby="sample-title">
                    <div className="sample-window">
                        <header className="sample-header">
                            <span className="sample-app"><SiteMark />Sentinel</span>
                            <span>Interactive demo</span>
                        </header>
                        <div className="sample-body">
                            <div className="sample-title">
                                <h2 id="sample-title">Downloads</h2>
                                <p>{applied ? 'Changes applied' : 'Review proposed moves'}</p>
                            </div>
                            <ul className="sample-files">
                                {files.map(({ name, folder, icon: Icon }, index) => (
                                    <li key={name} className={applied && selected[index] ? 'sample-file-moved' : undefined}>
                                        <label>
                                            <input type="checkbox" checked={selected[index]} disabled={applied}
                                                aria-label={`Move ${name}`}
                                                onChange={event => setSelected(values => values.map((value, i) => i === index ? event.target.checked : value))} />
                                            <span className="sample-file"><Icon size={17} aria-hidden />{name}</span>
                                            <span className="sample-destination">
                                                {applied && selected[index] ? <Check size={14} aria-hidden /> : <ArrowRight size={14} aria-hidden />}
                                                {selected[index] ? (applied ? `Moved to ${folder}` : folder) : 'Keep in Downloads'}
                                            </span>
                                        </label>
                                    </li>
                                ))}
                            </ul>
                            <footer className="sample-footer">
                                <p role="status">{applied ? `${count} sample ${count === 1 ? 'file moved' : 'files moved'}` : `${count} of ${files.length} selected`}</p>
                                <button className="site-button site-button-small" type="button" disabled={!count} onClick={() => setApplied(!applied)}>
                                    {applied ? <>Undo moves <RotateCcw size={15} aria-hidden /></> : `Apply ${count} ${count === 1 ? 'move' : 'moves'}`}
                                </button>
                            </footer>
                        </div>
                    </div>
                </section>
            </div>
        </>
    );
}
