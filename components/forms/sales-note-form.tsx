"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { X, Plus, Trash2 } from "lucide-react"

interface SalesNoteFormProps {
  note?: any
  onClose: () => void
}

export default function SalesNoteForm({ note, onClose }: SalesNoteFormProps) {
  const [clients, setClients] = useState<any[]>([])
  const [products, setProducts] = useState<any[]>([])
  const [formData, setFormData] = useState({
    id_cliente: 0,
    observaciones: "",
  })
  const [details, setDetails] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchClients()
    fetchProducts()
  }, [])

  const fetchClients = async () => {
    try {
      const response = await fetch("/api/clients")
      const data = await response.json()
      setClients(data)
    } catch (error) {
      console.error("Error fetching clients:", error)
    }
  }

  const fetchProducts = async () => {
    try {
      const response = await fetch("/api/products")
      const data = await response.json()
      setProducts(data)
    } catch (error) {
      console.error("Error fetching products:", error)
    }
  }

  const addDetail = () => {
    setDetails([
      ...details,
      {
        id_producto: 0,
        cantidad: 1,
        precio_unitario: 0,
        color: "",
        talla: "",
      },
    ])
  }

  const removeDetail = (index: number) => {
    setDetails(details.filter((_, i) => i !== index))
  }

  const updateDetail = (index: number, field: string, value: any) => {
    const newDetails = [...details]
    newDetails[index] = { ...newDetails[index], [field]: value }
    setDetails(newDetails)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch("/api/sales-notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          details,
        }),
      })

      if (response.ok) {
        alert("Nota de venta creada")
        onClose()
      }
    } catch (error) {
      console.error("Error:", error)
      alert("Error al crear la nota de venta")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
      <Card className="w-full max-w-2xl p-6 my-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-foreground">Nueva Nota de Venta</h2>
          <button onClick={onClose} className="text-muted hover:text-foreground">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Cliente</label>
            <select
              required
              value={formData.id_cliente}
              onChange={(e) => setFormData({ ...formData, id_cliente: Number.parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-border rounded-md"
            >
              <option value={0}>Seleccionar cliente</option>
              {clients.map((client) => (
                <option key={client.id_cliente} value={client.id_cliente}>
                  {client.nombre}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Observaciones</label>
            <textarea
              value={formData.observaciones}
              onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
              placeholder="Observaciones"
              className="w-full px-3 py-2 border border-border rounded-md"
              rows={3}
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="block text-sm font-medium text-foreground">Productos</label>
              <Button type="button" size="sm" onClick={addDetail} className="gap-1">
                <Plus size={16} />
                Agregar Producto
              </Button>
            </div>

            <div className="space-y-3 max-h-64 overflow-y-auto">
              {details.map((detail, index) => (
                <div key={index} className="p-3 border border-border rounded-md space-y-2">
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      required
                      value={detail.id_producto}
                      onChange={(e) => updateDetail(index, "id_producto", Number.parseInt(e.target.value))}
                      className="px-2 py-1 border border-border rounded text-sm"
                    >
                      <option value={0}>Seleccionar producto</option>
                      {products.map((product) => (
                        <option key={product.id_producto} value={product.id_producto}>
                          {product.nombre}
                        </option>
                      ))}
                    </select>
                    <Input
                      type="number"
                      placeholder="Cantidad"
                      value={detail.cantidad}
                      onChange={(e) => updateDetail(index, "cantidad", Number.parseInt(e.target.value))}
                      className="text-sm"
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="Precio"
                      value={detail.precio_unitario}
                      onChange={(e) => updateDetail(index, "precio_unitario", Number.parseFloat(e.target.value))}
                      className="text-sm"
                    />
                    <Input
                      placeholder="Color"
                      value={detail.color}
                      onChange={(e) => updateDetail(index, "color", e.target.value)}
                      className="text-sm"
                    />
                    <Input
                      placeholder="Talla"
                      value={detail.talla}
                      onChange={(e) => updateDetail(index, "talla", e.target.value)}
                      className="text-sm"
                    />
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => removeDetail(index)}
                    className="w-full text-destructive"
                  >
                    <Trash2 size={16} />
                    Eliminar
                  </Button>
                </div>
              ))}
            </div>
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
