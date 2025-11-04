"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Edit2, Trash2, Search, Eye } from "lucide-react"
import SalesNoteForm from "@/components/forms/sales-note-form"

interface SalesNote {
  id_nota: number
  id_cliente: number
  cliente_nombre: string
  fecha: string
  total: number
  estado: string
  estado_pedido: string
}

export default function SalesNotesModule() {
  const [notes, setNotes] = useState<SalesNote[]>([])
  const [filteredNotes, setFilteredNotes] = useState<SalesNote[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [editingNote, setEditingNote] = useState<SalesNote | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    fetchNotes()
  }, [page])

  const fetchNotes = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/sales-notes?page=${page}&search=${searchTerm}`)
      const data = await response.json()
      setNotes(data.notes)
      setTotalPages(data.totalPages)
    } catch (error) {
      console.error("Error fetching notes:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (confirm("¿Estás seguro de que deseas eliminar esta nota de venta?")) {
      try {
        await fetch(`/api/sales-notes/${id}`, { method: "DELETE" })
        fetchNotes()
      } catch (error) {
        console.error("Error deleting note:", error)
      }
    }
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingNote(null)
    fetchNotes()
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Notas de Venta</h1>
          <p className="text-muted mt-2">Gestiona tus notas de venta</p>
        </div>
        <Button
          onClick={() => {
            setEditingNote(null)
            setShowForm(true)
          }}
          className="gap-2"
        >
          <Plus size={18} />
          Nueva Nota
        </Button>
      </div>

      {showForm && <SalesNoteForm note={editingNote} onClose={handleFormClose} />}

      <Card className="p-6">
        <div className="mb-6 flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-muted" size={18} />
            <Input
              placeholder="Buscar por cliente o ID..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setPage(1)
              }}
              className="pl-10"
            />
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8 text-muted">Cargando notas...</div>
        ) : notes.length === 0 ? (
          <div className="text-center py-8 text-muted">No hay notas de venta registradas</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-semibold text-foreground">ID</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Cliente</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Fecha</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Total</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Estado</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Estado Pedido</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {notes.map((note) => (
                    <tr key={note.id_nota} className="border-b border-border hover:bg-card">
                      <td className="py-3 px-4 text-foreground font-medium">{note.id_nota}</td>
                      <td className="py-3 px-4 text-foreground">{note.cliente_nombre}</td>
                      <td className="py-3 px-4 text-foreground">{note.fecha}</td>
                      <td className="py-3 px-4 text-foreground font-medium">S/. {note.total.toFixed(2)}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            note.estado === "Cancelado"
                              ? "bg-green-100 text-green-700"
                              : "bg-yellow-100 text-yellow-700"
                          }`}
                        >
                          {note.estado}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                          {note.estado_pedido}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            <Eye size={16} />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingNote(note)
                              setShowForm(true)
                            }}
                          >
                            <Edit2 size={16} />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-destructive bg-transparent"
                            onClick={() => handleDelete(note.id_nota)}
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

            <div className="mt-6 flex justify-between items-center">
              <p className="text-sm text-muted">
                Página {page} de {totalPages}
              </p>
              <div className="flex gap-2">
                <Button variant="outline" disabled={page === 1} onClick={() => setPage(page - 1)}>
                  Anterior
                </Button>
                <Button variant="outline" disabled={page === totalPages} onClick={() => setPage(page + 1)}>
                  Siguiente
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
