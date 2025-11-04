import { type NextRequest, NextResponse } from "next/server"

const clients: any[] = []

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  const data = await request.json()
  const id = Number.parseInt(params.id)

  const index = clients.findIndex((c) => c.id_cliente === id)
  if (index !== -1) {
    clients[index] = { ...clients[index], ...data }
    return NextResponse.json(clients[index])
  }

  return NextResponse.json({ error: "Not found" }, { status: 404 })
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const id = Number.parseInt(params.id)
  const index = clients.findIndex((c) => c.id_cliente === id)

  if (index !== -1) {
    clients.splice(index, 1)
    return NextResponse.json({ success: true })
  }

  return NextResponse.json({ error: "Not found" }, { status: 404 })
}
