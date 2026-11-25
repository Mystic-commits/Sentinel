// Keep the local credential in memory for this dashboard session.
let accessToken = '';

export function setAccessToken(token: string) {
    accessToken = token;
}

export function getAccessToken() {
    return accessToken;
}
