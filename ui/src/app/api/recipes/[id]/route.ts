import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../../getBackendUrl";

export async function PUT(req: NextRequest) {
  // Extract ID from URL path
  const pathParts = req.nextUrl.pathname.split('/');
  const id = pathParts[pathParts.length - 1];

  const body = await req.text();
  const backendRes = await fetch(`${getBackendUrl()}/api/recipes/${id}`, {
    method: "PUT",
    headers: {
      "content-type": req.headers.get("content-type") || "application/json",
    },
    body,
  });
  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}

export async function DELETE(req: NextRequest) {
  // Extract ID from URL path
  const pathParts = req.nextUrl.pathname.split('/');
  const id = pathParts[pathParts.length - 1];

  const backendRes = await fetch(`${getBackendUrl()}/api/recipes/${id}`, {
    method: "DELETE",
  });
  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
