"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { BarChart3 } from "lucide-react"

interface ReportData {
  totalSales: number
  totalProfit: number
  totalCost: number
  salesCount: number
}

export default function SalesReportsModule() {
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [loading, setLoading] = useState(false)

  const generateReport = async () => {
    if (!startDate || !endDate) {
      alert("Por favor selecciona ambas fechas")
      return
    }

    try {
      setLoading(true)
      const response = await fetch(`/api/reports?startDate=${startDate}&endDate=${endDate}`)
      const data = await response.json()
      setReportData(data)
    } catch (error) {
      console.error("Error generating report:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Reportes y Ganancias</h1>
        <p className="text-muted mt-2">Analiza tus ventas y ganancias</p>
      </div>

      <Card className="p-6 mb-8">
        <h2 className="text-lg font-bold text-foreground mb-4">Filtrar por Fechas</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Fecha Inicio</label>
            <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Fecha Fin</label>
            <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <div className="flex items-end">
            <Button onClick={generateReport} disabled={loading} className="w-full gap-2">
              <BarChart3 size={18} />
              {loading ? "Generando..." : "Generar Reporte"}
            </Button>
          </div>
        </div>
      </Card>

      {reportData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <p className="text-sm text-blue-600 font-medium">Total de Ventas</p>
            <p className="text-3xl font-bold text-blue-900 mt-2">S/. {reportData.totalSales.toFixed(2)}</p>
          </Card>
          <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <p className="text-sm text-green-600 font-medium">Ganancia Total</p>
            <p className="text-3xl font-bold text-green-900 mt-2">S/. {reportData.totalProfit.toFixed(2)}</p>
          </Card>
          <Card className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <p className="text-sm text-orange-600 font-medium">Costo Total</p>
            <p className="text-3xl font-bold text-orange-900 mt-2">S/. {reportData.totalCost.toFixed(2)}</p>
          </Card>
          <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <p className="text-sm text-purple-600 font-medium">Número de Ventas</p>
            <p className="text-3xl font-bold text-purple-900 mt-2">{reportData.salesCount}</p>
          </Card>
        </div>
      )}
    </div>
  )
}
