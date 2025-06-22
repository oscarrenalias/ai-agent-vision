import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../getBackendUrl";

export async function GET() {
  // Proxy GET /api/recipes to backend
  const backendRes = await fetch(`${getBackendUrl()}/api/recipes`);
  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
