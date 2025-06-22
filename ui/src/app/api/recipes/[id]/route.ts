import { NextRequest, NextResponse } from "next/server";
import { getBackendUrl } from "../../getBackendUrl";

export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const { id } = params;
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

export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const { id } = params;
  const backendRes = await fetch(`${getBackendUrl()}/api/recipes/${id}`, {
    method: "DELETE",
  });
  // 204 returns no content, so don't try to parse JSON
  if (backendRes.status === 204) {
    return new NextResponse(null, { status: 204 });
  }
  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
