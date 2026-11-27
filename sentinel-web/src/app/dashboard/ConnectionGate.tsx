'use client';

import Link from 'next/link';
import SiteMark from '@/components/landing/SiteMark';
import { invoke, isTauri } from '@tauri-apps/api/core';
import { FormEvent, useEffect, useState, useSyncExternalStore } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { api } from '@/lib/api/client';
import { setAccessToken, setDesktopConnection } from '@/lib/api/access';

const subscribeToShell = () => () => {};
const browserSnapshot = () => false;

function ConnectedDashboard({ children }: { children: React.ReactNode }) {
    useWebSocket();
    return <>{children}</>;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState('');
    const [connected, setConnected] = useState(false);

    const [connecting, setConnecting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const desktop = useSyncExternalStore(subscribeToShell, isTauri, browserSnapshot);

    useEffect(() => {
        if (!desktop) return;
        let cancelled = false;

        async function start() {
            try {
                for (let attempt = 0; attempt < 80 && !cancelled; attempt++) {
                    const connection = await invoke<{ port: number; token: string } | null>('desktop_connection');
                    if (cancelled) return;
                    if (connection) {
                        setDesktopConnection(connection.port, connection.token);
                        await api.getTasks();
                        if (!cancelled) setConnected(true);
                        return;
                    }
                    await new Promise(resolve => setTimeout(resolve, 250));
                }
                throw new Error('Sentinel took too long to start. Close and reopen the app to retry.');
            } catch (error) {
                if (!cancelled) setError(error instanceof Error ? error.message : String(error));
            }
        }
        void start();
        return () => { cancelled = true; };
    }, [desktop]);

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

    if (desktop) {
        return (
            <main className="mx-auto max-w-lg px-5 py-14 sm:py-24">
                <div className="mb-9 flex items-center gap-2.5 text-xl font-extrabold"><SiteMark />Sentinel</div>
                <h1 className="mb-3 text-3xl font-extrabold">{error ? 'Could not open the workspace' : 'Opening workspace…'}</h1>
                {error && <p role="alert" className="text-txt-secondary">{error}</p>}
            </main>
        );
    }

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
            <Link href="/docs" className="mt-6 inline-block text-sm font-semibold underline">Local setup guide</Link>
        </main>
    );
}
