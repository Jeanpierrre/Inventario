import { type NextRequest, NextResponse } from "next/server"

const products: any[] = []

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  const data = await request.json()
  const id = Number.parseInt(params.id)

  const index = products.findIndex((p) => p.id_producto === id)
  if (index !== -1) {
    products[index] = { ...products[index], ...data }
    return NextResponse.json(products[index])
  }

  return NextResponse.json({ error: "Not found" }, { status: 404 })
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const id = Number.parseInt(params.id)
  const index = products.findIndex((p) => p.id_producto === id)

  if (index !== -1) {
    products.splice(index, 1)
    return NextResponse.json({ success: true })
  }

  return NextResponse.json({ error: "Not found" }, { status: 404 })
}
