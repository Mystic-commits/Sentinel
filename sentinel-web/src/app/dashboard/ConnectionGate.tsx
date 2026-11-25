'use client';

import SiteMark from '@/components/landing/SiteMark';
import { FormEvent, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { api } from '@/lib/api/client';
import { setAccessToken } from '@/lib/api/access';

function ConnectedDashboard({ children }: { children: React.ReactNode }) {
    useWebSocket();
    return <>{children}</>;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState('');
    const [connected, setConnected] = useState(false);

    const [connecting, setConnecting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function connect(event: FormEvent) {
        event.preventDefault();
        setConnecting(true);
        setError(null);
        setAccessToken(token);
        try {
            await api.getTasks();
            setToken('');
            setConnected(true);
        } catch {
            setAccessToken('');
            setError('Could not connect. Check that Sentinel is running and the token matches.');
        } finally {
            setConnecting(false);
        }
    }

    if (connected) return <ConnectedDashboard>{children}</ConnectedDashboard>;

    return (
        <main className="mx-auto max-w-lg px-5 py-14 sm:py-24">
            <div className="mb-9 flex items-center gap-2.5 text-xl font-extrabold tracking-tight"><SiteMark />Sentinel</div>
            <h1 className="mb-3 text-4xl font-extrabold tracking-[-0.055em] sm:text-5xl">Open your workspace.</h1>
            <p className="mb-7 text-txt-secondary">Paste the access token from the terminal where you started the Sentinel backend.</p>
            <form onSubmit={connect} className="grid gap-4">
                <label className="grid gap-2 text-sm font-bold">
                    Local access token
                    <input type="password" autoComplete="off" required
                        pattern="[a-fA-F0-9]{64}" value={token}
                        onChange={(event) => setToken(event.target.value)}
                        className="workspace-input p-3 text-base" />
                </label>
                {error && <p role="alert">{error}</p>}
                <button disabled={connecting} className="workspace-action justify-self-start">
                    {connecting ? 'Connecting…' : 'Connect'}
                </button>
            </form>
        </main>
    );
}
