import { NextResponse } from "next/server"

export async function GET() {
  // This would calculate from database
  return NextResponse.json({ cost: 0 })
}
