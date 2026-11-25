'use client';

import { useState } from 'react';

export default function CopyCommands({ commands }: { commands: string }) {
    const [feedback, setFeedback] = useState('');

    async function copy() {
        try {
            await navigator.clipboard.writeText(commands);
            setFeedback('Commands copied.');
        } catch {
            setFeedback('Clipboard unavailable. Select the commands to copy them.');
        }
    }

    return (
        <div className="site-code">
            <div className="site-code-toolbar">
                <span role="status">{feedback}</span>
                <button type="button" onClick={() => void copy()}>Copy commands</button>
            </div>
            <pre><code>{commands}</code></pre>
        </div>
    );
}
