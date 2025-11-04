import { type NextRequest, NextResponse } from "next/server"

const salesNotes: any[] = []

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const page = Number.parseInt(searchParams.get("page") || "1")
  const search = searchParams.get("search") || ""

  const filtered = salesNotes.filter(
    (note) =>
      note.cliente_nombre.toLowerCase().includes(search.toLowerCase()) || note.id_nota.toString().includes(search),
  )

  const perPage = 10
  const totalPages = Math.ceil(filtered.length / perPage)
  const start = (page - 1) * perPage
  const notes = filtered.slice(start, start + perPage)

  return NextResponse.json({ notes, totalPages })
}

export async function POST(request: NextRequest) {
  const data = await request.json()

  const newNote = {
    id_nota: salesNotes.length + 1,
    ...data,
    fecha: new Date().toISOString().split("T")[0],
    estado: "Pendiente",
    estado_pedido: "ABIERTO",
  }

  salesNotes.push(newNote)
  return NextResponse.json(newNote, { status: 201 })
}
