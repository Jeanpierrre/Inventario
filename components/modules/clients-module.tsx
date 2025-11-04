"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Edit2, Trash2, Search, Users } from "lucide-react"
import ClientForm from "@/components/forms/client-form"

interface Client {
  id_cliente: number
  nombre: string
  dni: string
  direccion: string
  telefono: string
}

export default function ClientsModule() {
  const [clients, setClients] = useState<Client[]>([])
  const [filteredClients, setFilteredClients] = useState<Client[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [editingClient, setEditingClient] = useState<Client | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchClients()
  }, [])

  useEffect(() => {
    const filtered = clients.filter(
      (client) =>
        client.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.dni.includes(searchTerm) ||
        client.id_cliente.toString().includes(searchTerm),
    )
    setFilteredClients(filtered)
  }, [searchTerm, clients])

  const fetchClients = async () => {
    try {
      setLoading(true)
      const response = await fetch("/api/clients")
      if (response.ok) {
        const data = await response.json()
        setClients(data)
      }
    } catch (error) {
      console.error("Error fetching clients:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (confirm("¿Estás seguro de que deseas eliminar este cliente?")) {
      try {
        await fetch(`/api/clients/${id}`, { method: "DELETE" })
        fetchClients()
      } catch (error) {
        console.error("Error deleting client:", error)
      }
    }
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingClient(null)
    fetchClients()
  }

  return (
    <div className="flex-1 overflow-auto bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <div className="p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-8 animate-fade-in">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
                <Users className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">
                Gestión de Clientes
              </h1>
            </div>
            <p className="text-slate-600 ml-11">Administra tu base de clientes</p>
          </div>
          <Button
            onClick={() => {
              setEditingClient(null)
              setShowForm(true)
            }}
            className="gap-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-medium"
          >
            <Plus size={18} />
            Nuevo Cliente
          </Button>
        </div>

        {showForm && <ClientForm client={editingClient} onClose={handleFormClose} />}

        {/* Search Card */}
        <Card className="p-6 mb-6 border-0 bg-white hover:shadow-lg transition-all duration-300">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <Input
                placeholder="Buscar por nombre, DNI o ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 border-slate-200 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div className="text-sm text-slate-600 font-medium px-4 py-2 bg-slate-50 rounded-lg">
              {filteredClients.length} cliente{filteredClients.length !== 1 ? "s" : ""}
            </div>
          </div>
        </Card>

        {/* Clients Table */}
        <Card className="border-0 bg-white overflow-hidden hover:shadow-lg transition-all duration-300">
          {loading ? (
            <div className="text-center py-12 text-slate-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
              <p>Cargando clientes...</p>
            </div>
          ) : filteredClients.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No hay clientes registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">ID</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Nombre</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">DNI</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Teléfono</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Dirección</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredClients.map((client, idx) => (
                    <tr
                      key={client.id_cliente}
                      className={`border-b border-slate-100 hover:bg-blue-50 transition-colors ${idx % 2 === 0 ? "bg-white" : "bg-slate-50/50"}`}
                    >
                      <td className="py-4 px-6 text-slate-900 font-medium">#{client.id_cliente}</td>
                      <td className="py-4 px-6 text-slate-900 font-medium">{client.nombre}</td>
                      <td className="py-4 px-6 text-slate-600">{client.dni}</td>
                      <td className="py-4 px-6 text-slate-600">{client.telefono}</td>
                      <td className="py-4 px-6 text-slate-600 text-sm">{client.direccion}</td>
                      <td className="py-4 px-6">
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingClient(client)
                              setShowForm(true)
                            }}
                            className="border-blue-200 text-blue-600 hover:bg-blue-50"
                          >
                            <Edit2 size={16} />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(client.id_cliente)}
                            className="border-red-200 text-red-600 hover:bg-red-50"
                          >
                            <Trash2 size={16} />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
