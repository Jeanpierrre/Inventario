"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Edit2, Trash2, Search, Package } from "lucide-react"
import ProductForm from "@/components/forms/product-form"

interface Product {
  id_producto: number
  nombre: string
  stock: number
  costo: number
  precio_inicial: number
}

export default function ProductsModule() {
  const [products, setProducts] = useState<Product[]>([])
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [inventoryCost, setInventoryCost] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProducts()
  }, [])

  useEffect(() => {
    const filtered = products.filter(
      (product) =>
        product.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.id_producto.toString().includes(searchTerm),
    )
    setFilteredProducts(filtered)
  }, [searchTerm, products])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const [productsRes, costRes] = await Promise.all([fetch("/api/products"), fetch("/api/products/inventory-cost")])
      if (productsRes.ok && costRes.ok) {
        const productsData = await productsRes.json()
        const costData = await costRes.json()
        setProducts(productsData)
        setInventoryCost(costData.cost)
      }
    } catch (error) {
      console.error("Error fetching products:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (confirm("¿Estás seguro de que deseas eliminar este producto?")) {
      try {
        await fetch(`/api/products/${id}`, { method: "DELETE" })
        fetchProducts()
      } catch (error) {
        console.error("Error deleting product:", error)
      }
    }
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingProduct(null)
    fetchProducts()
  }

  const totalStock = products.reduce((sum, p) => sum + p.stock, 0)

  return (
    <div className="flex-1 overflow-auto bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <div className="p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-8 animate-fade-in">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg">
                <Package className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-emerald-700 bg-clip-text text-transparent">
                Gestión de Productos
              </h1>
            </div>
            <p className="text-slate-600 ml-11">Administra tu inventario</p>
          </div>
          <Button
            onClick={() => {
              setEditingProduct(null)
              setShowForm(true)
            }}
            className="gap-2 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white font-medium"
          >
            <Plus size={18} />
            Nuevo Producto
          </Button>
        </div>

        {showForm && <ProductForm product={editingProduct} onClose={handleFormClose} />}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="p-6 border-0 bg-white hover:shadow-lg transition-all duration-300">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-600 font-medium">Costo Total Inventario</p>
                <p className="text-3xl font-bold text-slate-900 mt-2">S/. {inventoryCost.toFixed(2)}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Package className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>
          <Card className="p-6 border-0 bg-white hover:shadow-lg transition-all duration-300">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-600 font-medium">Total de Productos</p>
                <p className="text-3xl font-bold text-slate-900 mt-2">{products.length}</p>
              </div>
              <div className="p-3 bg-emerald-100 rounded-lg">
                <Package className="w-6 h-6 text-emerald-600" />
              </div>
            </div>
          </Card>
          <Card className="p-6 border-0 bg-white hover:shadow-lg transition-all duration-300">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-600 font-medium">Stock Total</p>
                <p className="text-3xl font-bold text-slate-900 mt-2">{totalStock}</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <Package className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Search Card */}
        <Card className="p-6 mb-6 border-0 bg-white hover:shadow-lg transition-all duration-300">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <Input
                placeholder="Buscar por nombre o ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 border-slate-200 focus:border-emerald-500 focus:ring-emerald-500"
              />
            </div>
            <div className="text-sm text-slate-600 font-medium px-4 py-2 bg-slate-50 rounded-lg">
              {filteredProducts.length} producto{filteredProducts.length !== 1 ? "s" : ""}
            </div>
          </div>
        </Card>

        {/* Products Table */}
        <Card className="border-0 bg-white overflow-hidden hover:shadow-lg transition-all duration-300">
          {loading ? (
            <div className="text-center py-12 text-slate-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mb-3"></div>
              <p>Cargando productos...</p>
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No hay productos registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">ID</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Nombre</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Stock</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Costo</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Precio Inicial</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-900">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProducts.map((product, idx) => (
                    <tr
                      key={product.id_producto}
                      className={`border-b border-slate-100 hover:bg-emerald-50 transition-colors ${idx % 2 === 0 ? "bg-white" : "bg-slate-50/50"}`}
                    >
                      <td className="py-4 px-6 text-slate-900 font-medium">#{product.id_producto}</td>
                      <td className="py-4 px-6 text-slate-900 font-medium">{product.nombre}</td>
                      <td className="py-4 px-6">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${product.stock > 0 ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}
                        >
                          {product.stock}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-slate-600">S/. {product.costo.toFixed(2)}</td>
                      <td className="py-4 px-6 text-slate-600">S/. {product.precio_inicial?.toFixed(2) || "N/A"}</td>
                      <td className="py-4 px-6">
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingProduct(product)
                              setShowForm(true)
                            }}
                            className="border-emerald-200 text-emerald-600 hover:bg-emerald-50"
                          >
                            <Edit2 size={16} />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(product.id_producto)}
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
