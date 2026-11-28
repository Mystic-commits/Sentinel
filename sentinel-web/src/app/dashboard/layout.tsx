import '@fontsource-variable/manrope';
import '@fontsource/ibm-plex-mono/latin-400.css';
import './workspace.css';
import type { Metadata } from 'next';
import ConnectionGate from './ConnectionGate';

export const metadata: Metadata = {
    title: 'Sentinel Local Dashboard',
    robots: { index: false, follow: false },
};

export default function Layout({ children }: { children: React.ReactNode }) {
    return <div className="workspace"><ConnectionGate>{children}</ConnectionGate></div>;
}
