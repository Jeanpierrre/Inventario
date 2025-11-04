"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Users, Package, FileText, TrendingUp, ArrowUpRight, ArrowDownRight } from "lucide-react"

interface DashboardStats {
  totalClients: number
  totalProducts: number
  totalSalesNotes: number
  inventoryCost: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalClients: 0,
    totalProducts: 0,
    totalSalesNotes: 0,
    inventoryCost: 0,
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/dashboard/stats")
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error("Error fetching stats:", error)
    }
  }

  const statCards = [
    {
      title: "Clientes",
      value: stats.totalClients,
      icon: Users,
      gradient: "from-blue-500 to-blue-600",
      bgGradient: "from-blue-50 to-blue-100",
      trend: "+12%",
      positive: true,
    },
    {
      title: "Productos",
      value: stats.totalProducts,
      icon: Package,
      gradient: "from-emerald-500 to-emerald-600",
      bgGradient: "from-emerald-50 to-emerald-100",
      trend: "+8%",
      positive: true,
    },
    {
      title: "Notas de Venta",
      value: stats.totalSalesNotes,
      icon: FileText,
      gradient: "from-purple-500 to-purple-600",
      bgGradient: "from-purple-50 to-purple-100",
      trend: "+24%",
      positive: true,
    },
    {
      title: "Costo Inventario",
      value: `S/. ${stats.inventoryCost.toFixed(2)}`,
      icon: TrendingUp,
      gradient: "from-orange-500 to-orange-600",
      bgGradient: "from-orange-50 to-orange-100",
      trend: "-3%",
      positive: false,
    },
  ]

  return (
    <div className="flex-1 overflow-auto bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <div className="p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-emerald-600 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-slate-600 mt-2">Bienvenido a Sexy Boom - Sistema de Gestión de Ventas</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div key={index} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-0 bg-white">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg bg-gradient-to-br ${stat.bgGradient}`}>
                      <Icon className={`w-6 h-6 bg-gradient-to-r ${stat.gradient} bg-clip-text text-transparent`} />
                    </div>
                    <div
                      className={`flex items-center gap-1 text-xs font-semibold ${stat.positive ? "text-emerald-600" : "text-red-600"}`}
                    >
                      {stat.positive ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                      {stat.trend}
                    </div>
                  </div>
                  <p className="text-sm text-slate-600 font-medium">{stat.title}</p>
                  <p className="text-3xl font-bold text-slate-900 mt-2">{stat.value}</p>
                </Card>
              </div>
            )
          })}
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <Card className="lg:col-span-2 p-6 border-0 bg-white hover:shadow-lg transition-all duration-300">
            <h2 className="text-lg font-bold text-slate-900 mb-6">Acciones Rápidas</h2>
            <div className="grid grid-cols-2 gap-4">
              {[
                { icon: Users, label: "Agregar Cliente", color: "from-blue-500 to-blue-600" },
                { icon: Package, label: "Registrar Producto", color: "from-emerald-500 to-emerald-600" },
                { icon: FileText, label: "Nueva Venta", color: "from-purple-500 to-purple-600" },
                { icon: TrendingUp, label: "Ver Reportes", color: "from-orange-500 to-orange-600" },
              ].map((action, idx) => {
                const ActionIcon = action.icon
                return (
                  <button
                    key={idx}
                    className={`p-4 rounded-lg bg-gradient-to-br ${action.color} text-white font-medium hover:shadow-lg transition-all duration-200 hover:scale-105`}
                  >
                    <ActionIcon className="w-5 h-5 mb-2" />
                    <p className="text-xs">{action.label}</p>
                  </button>
                )
              })}
            </div>
          </Card>

          {/* Info Card */}
          <Card className="p-6 border-0 bg-gradient-to-br from-indigo-50 to-emerald-50 hover:shadow-lg transition-all duration-300">
            <h2 className="text-lg font-bold text-slate-900 mb-4">Información</h2>
            <p className="text-sm text-slate-700 leading-relaxed">
              Sexy Boom es tu solución completa para gestionar ventas, inventario y reportes financieros de tu negocio.
            </p>
            <div className="mt-6 pt-6 border-t border-slate-200">
              <p className="text-xs text-slate-600 font-medium">Versión 1.0</p>
              <p className="text-xs text-slate-500 mt-1">© 2025 Sexy Boom</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
