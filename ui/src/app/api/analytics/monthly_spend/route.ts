import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../../getBackendUrl";

export async function GET(req: NextRequest) {
  // Extract year and month from query params
  const { searchParams } = new URL(req.url);
  const year = searchParams.get("year");
  const month = searchParams.get("month");

  // Build backend URL with query params
  let backendUrl = `${getBackendUrl()}/api/analytics/monthly_spend`;
  if (year && month) {
    backendUrl += `?year=${encodeURIComponent(year)}&month=${encodeURIComponent(
      month
    )}`;
  }

  // Proxy GET requests to the backend analytics endpoint
  const backendRes = await fetch(backendUrl, {
    method: "GET",
    headers: {
      accept: "application/json",
    },
  });

  // If backend returns no content, return empty structure
  if (backendRes.status === 404 || backendRes.status === 204) {
    return NextResponse.json(
      { monthly_spend: { overall: [], level_1: [], level_2: [] } },
      { status: 200 }
    );
  }

  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
