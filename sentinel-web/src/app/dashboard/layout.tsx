import type { Metadata } from 'next';
import ConnectionGate from './ConnectionGate';

export const metadata: Metadata = {
    title: 'Sentinel Local Dashboard',
    robots: { index: false, follow: false },
};

export default function Layout({ children }: { children: React.ReactNode }) {
    return <ConnectionGate>{children}</ConnectionGate>;
}
