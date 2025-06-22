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
  context: { params: { id: string } }
) {
  const { id } = await context.params;
  const backendRes = await fetch(`${getBackendUrl()}/api/recipes/${id}`, {
    method: "DELETE",
  });
  const data = await backendRes.json();
  return NextResponse.json(data, { status: backendRes.status });
}
