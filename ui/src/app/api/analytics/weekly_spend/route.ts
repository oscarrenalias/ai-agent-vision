import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  // Proxy GET requests to the backend analytics endpoint
  const backendRes = await fetch(
    "http://localhost:8000/api/analytics/weekly_spend",
    {
      method: "GET",
      headers: {
        accept: "application/json",
      },
    }
  );

  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
