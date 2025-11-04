import { type NextRequest, NextResponse } from "next/server"

const products: any[] = []

export async function GET() {
  return NextResponse.json(products)
}

export async function POST(request: NextRequest) {
  const data = await request.json()

  const newProduct = {
    id_producto: products.length + 1,
    ...data,
  }

  products.push(newProduct)
  return NextResponse.json(newProduct, { status: 201 })
}
