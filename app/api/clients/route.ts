import { type NextRequest, NextResponse } from "next/server"

// Mock database - replace with real database
const clients: any[] = []

export async function GET() {
  return NextResponse.json(clients)
}

export async function POST(request: NextRequest) {
  const data = await request.json()

  const newClient = {
    id_cliente: clients.length + 1,
    ...data,
  }

  clients.push(newClient)
  return NextResponse.json(newClient, { status: 201 })
}
