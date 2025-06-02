// Helper to get the backend URL from environment or default
export function getBackendUrl(): string {
  // Use process.env.NEXT_PUBLIC_BACKEND_URL if available, otherwise default
  return (typeof process !== "undefined" && process.env?.NEXT_PUBLIC_BACKEND_URL)
    ? process.env.NEXT_PUBLIC_BACKEND_URL
    : "http://localhost:8000";
}
