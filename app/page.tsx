"use client"

import { useState } from "react"
import LoginPage from "@/components/auth/login-page"
import Dashboard from "@/components/modules/dashboard"
import Sidebar from "@/components/layout/sidebar"
import ClientsModule from "@/components/modules/clients-module"
import ProductsModule from "@/components/modules/products-module"
import SalesNotesModule from "@/components/modules/sales-notes-module"
import SalesReportsModule from "@/components/modules/sales-reports-module"

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activeModule, setActiveModule] = useState("dashboard")

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />
  }

  const renderModule = () => {
    switch (activeModule) {
      case "dashboard":
        return <Dashboard />
      case "clients":
        return <ClientsModule />
      case "products":
        return <ProductsModule />
      case "sales-notes":
        return <SalesNotesModule />
      case "reports":
        return <SalesReportsModule />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        activeModule={activeModule}
        setActiveModule={setActiveModule}
        onLogout={() => setIsAuthenticated(false)}
      />
      <main className="flex-1 overflow-auto">{renderModule()}</main>
    </div>
  )
}
