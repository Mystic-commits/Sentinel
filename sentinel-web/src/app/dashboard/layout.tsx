/**
 * Dashboard Layout
 * 
 * Three-panel layout with WebSocket provider.
 */

'use client';

import { useWebSocket } from '@/hooks/useWebSocket';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    // Initialize WebSocket connection
    useWebSocket();

    return <>{children}</>;
}
