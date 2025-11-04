"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { X } from "lucide-react"

interface ProductFormProps {
  product?: any
  onClose: () => void
}

export default function ProductForm({ product, onClose }: ProductFormProps) {
  const [formData, setFormData] = useState({
    nombre: "",
    stock: 0,
    costo: 0,
    precio_inicial: 0,
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (product) {
      setFormData({
        nombre: product.nombre,
        stock: product.stock,
        costo: product.costo,
        precio_inicial: product.precio_inicial || 0,
      })
    }
  }, [product])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const method = product ? "PUT" : "POST"
      const url = product ? `/api/products/${product.id_producto}` : "/api/products"

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        alert(product ? "Producto actualizado" : "Producto creado")
        onClose()
      }
    } catch (error) {
      console.error("Error:", error)
      alert("Error al guardar el producto")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-foreground">{product ? "Editar Producto" : "Nuevo Producto"}</h2>
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
              placeholder="Nombre del producto"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Stock</label>
            <Input
              required
              type="number"
              value={formData.stock}
              onChange={(e) => setFormData({ ...formData, stock: Number.parseInt(e.target.value) })}
              placeholder="Stock"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Costo</label>
            <Input
              required
              type="number"
              step="0.01"
              value={formData.costo}
              onChange={(e) => setFormData({ ...formData, costo: Number.parseFloat(e.target.value) })}
              placeholder="Costo"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Precio Inicial</label>
            <Input
              type="number"
              step="0.01"
              value={formData.precio_inicial}
              onChange={(e) => setFormData({ ...formData, precio_inicial: Number.parseFloat(e.target.value) })}
              placeholder="Precio Inicial"
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
