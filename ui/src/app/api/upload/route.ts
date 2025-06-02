import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../getBackendUrl";

export async function POST(req: NextRequest) {
  // Only handle /api/upload
  const backendRes = await fetch(`${getBackendUrl()}/api/upload`, {
    method: "POST",
    headers: {
      // Forward only the content-type header for multipart/form-data
      "content-type": req.headers.get("content-type") || "",
    },
    body: req.body,
    // Only add duplex in Node.js (development), and bypass type error
    ...(typeof process !== "undefined" && (process as any).versions?.node
      ? { duplex: "half" as any }
      : {}),
  });

  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
