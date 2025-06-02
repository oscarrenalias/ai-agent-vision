import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../../getBackendUrl";

export async function GET(req: NextRequest) {
  // Extract year from query params
  const { searchParams } = new URL(req.url);
  const year = searchParams.get("year");

  // Build backend URL with query param
  let backendUrl = `${getBackendUrl()}/api/analytics/yearly_monthly_spend`;
  if (year) {
    backendUrl += `?year=${encodeURIComponent(year)}`;
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
      { yearly_monthly_spend: { overall: [], level_1: [], level_2: [], level_3: [] } },
      { status: 200 }
    );
  }

  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
