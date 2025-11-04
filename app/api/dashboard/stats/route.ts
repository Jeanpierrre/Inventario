import { NextResponse } from "next/server"

export async function GET() {
  return NextResponse.json({
    totalClients: 0,
    totalProducts: 0,
    totalSalesNotes: 0,
    inventoryCost: 0,
  })
}
