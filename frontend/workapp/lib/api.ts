const serverApiBaseUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export function apiUrl(path: string): string {
  if (typeof window === "undefined") {
    return `${serverApiBaseUrl}${path}`;
  }

  return path;
}