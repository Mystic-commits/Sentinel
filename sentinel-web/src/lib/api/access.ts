// Keep the local credential in memory for this dashboard session.
let accessToken = '';

export function setAccessToken(token: string) {
    accessToken = token;
}

export function getAccessToken() {
    return accessToken;
}

let desktopPort: number | undefined;

export function setDesktopConnection(port: number, token: string) {
    desktopPort = port;
    setAccessToken(token);
}

export function getApiUrl() {
    return desktopPort
        ? `http://127.0.0.1:${desktopPort}/api`
        : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
}

export function getEventsUrl() {
    return desktopPort
        ? `ws://127.0.0.1:${desktopPort}/ws/events`
        : process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/events';
}
