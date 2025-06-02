import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../../getBackendUrl";

export async function GET(req: NextRequest) {
  // Proxy GET requests to the backend analytics endpoint
  const backendRes = await fetch(
    `${getBackendUrl()}/api/analytics/yearly_spend`,
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
