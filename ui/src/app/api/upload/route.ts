import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  // Only handle /api/upload
  const backendRes = await fetch("http://localhost:8000/api/upload", {
    method: "POST",
    headers: {
      // Forward only the content-type header for multipart/form-data
      "content-type": req.headers.get("content-type") || "",
    },
    body: req.body,
  });

  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
