"use client"

import { Users, Package, FileText, BarChart3, Home, LogOut, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SidebarProps {
  activeModule: string
  setActiveModule: (module: string) => void
  onLogout: () => void
}

export default function Sidebar({ activeModule, setActiveModule, onLogout }: SidebarProps) {
  const modules = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "clients", label: "Clientes", icon: Users },
    { id: "products", label: "Productos", icon: Package },
    { id: "sales-notes", label: "Notas de Venta", icon: FileText },
    { id: "reports", label: "Reportes", icon: BarChart3 },
  ]

  return (
    <aside className="w-64 bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white border-r border-slate-700 flex flex-col shadow-xl">
      {/* Header */}
      <div className="p-6 border-b border-slate-700 bg-gradient-to-r from-indigo-600/20 to-emerald-500/20">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-2 bg-gradient-to-br from-indigo-500 to-emerald-500 rounded-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent">
            Sexy Boom
          </h1>
        </div>
        <p className="text-xs text-slate-400 ml-9">Sistema de Gestión de Ventas</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {modules.map((module) => {
          const Icon = module.icon
          const isActive = activeModule === module.id
          return (
            <button
              key={module.id}
              onClick={() => setActiveModule(module.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive
                  ? "bg-gradient-to-r from-indigo-600 to-emerald-500 text-white shadow-lg shadow-indigo-500/20"
                  : "text-slate-300 hover:bg-slate-700/50 hover:text-white"
              }`}
            >
              <Icon size={20} />
              <span className="font-medium text-sm">{module.label}</span>
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700 bg-slate-900/50">
        <Button
          onClick={onLogout}
          className="w-full justify-center gap-2 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white font-medium transition-all duration-200"
        >
          <LogOut size={18} />
          Salir
        </Button>
      </div>
    </aside>
  )
}
