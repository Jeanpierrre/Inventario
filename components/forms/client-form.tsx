"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { X } from "lucide-react"

interface ClientFormProps {
  client?: any
  onClose: () => void
}

export default function ClientForm({ client, onClose }: ClientFormProps) {
  const [formData, setFormData] = useState({
    nombre: "",
    dni: "",
    direccion: "",
    telefono: "",
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (client) {
      setFormData({
        nombre: client.nombre,
        dni: client.dni,
        direccion: client.direccion,
        telefono: client.telefono,
      })
    }
  }, [client])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const method = client ? "PUT" : "POST"
      const url = client ? `/api/clients/${client.id_cliente}` : "/api/clients"

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        alert(client ? "Cliente actualizado" : "Cliente creado")
        onClose()
      }
    } catch (error) {
      console.error("Error:", error)
      alert("Error al guardar el cliente")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-foreground">{client ? "Editar Cliente" : "Nuevo Cliente"}</h2>
          <button onClick={onClose} className="text-muted hover:text-foreground">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Nombre</label>
            <Input
              required
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              placeholder="Nombre del cliente"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">DNI</label>
            <Input
              required
              value={formData.dni}
              onChange={(e) => setFormData({ ...formData, dni: e.target.value })}
              placeholder="DNI"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Teléfono</label>
            <Input
              value={formData.telefono}
              onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              placeholder="Teléfono"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Dirección</label>
            <Input
              value={formData.direccion}
              onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
              placeholder="Dirección"
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? "Guardando..." : "Guardar"}
            </Button>
            <Button type="button" variant="outline" onClick={onClose} className="flex-1 bg-transparent">
              Cancelar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
