'use client';

import { ShieldCheck } from 'lucide-react';
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
        <main className="mx-auto max-w-md px-5 py-16 sm:py-24">
            <ShieldCheck className="mb-4 text-[#a6edc3]" size={32} aria-hidden />
            <h1 className="mb-4 text-xl font-semibold">Connect to Sentinel</h1>
            <p className="mb-6 text-sm text-txt-muted">Paste the token printed in the terminal where you started the Sentinel backend.</p>
            <form onSubmit={connect} className="grid gap-4">
                <label className="grid gap-2">
                    Local access token
                    <input type="password" autoComplete="off" required
                        pattern="[a-fA-F0-9]{64}" value={token}
                        onChange={(event) => setToken(event.target.value)}
                        className="rounded border border-[#526c5e] bg-[#101c18] p-3" />
                </label>
                {error && <p role="alert">{error}</p>}
                <button disabled={connecting} className="rounded bg-[#a6edc3] p-3 font-semibold text-[#12241c]">
                    {connecting ? 'Connecting…' : 'Connect'}
                </button>
            </form>
        </main>
    );
}
