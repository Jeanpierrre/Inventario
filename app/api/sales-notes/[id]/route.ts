import { type NextRequest, NextResponse } from "next/server"

const salesNotes: any[] = []

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const id = Number.parseInt(params.id)
  const index = salesNotes.findIndex((n) => n.id_nota === id)

  if (index !== -1) {
    salesNotes.splice(index, 1)
    return NextResponse.json({ success: true })
  }

  return NextResponse.json({ error: "Not found" }, { status: 404 })
}
