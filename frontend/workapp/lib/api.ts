const serverApiBaseUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export function apiUrl(path: string): string {
    return `${serverApiBaseUrl}${path}`;

}