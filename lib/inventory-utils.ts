export interface Product {
  id_producto: number
  nombre: string
  stock: number
  costo: number
  precio_inicial: number
}

export interface Client {
  id_cliente: number
  nombre: string
  dni: string
  direccion: string
  telefono: string
}

// Validaciones
export function isValidDNI(dni: string): boolean {
  return /^\d{8}$/.test(dni)
}

export function isValidStock(stock: number): boolean {
  return stock >= 0 && Number.isInteger(stock)
}

export function isValidPrice(price: number): boolean {
  return price >= 0 && !isNaN(price)
}

// Cálculos
export function calculateTotalValue(products: Product[]): number {
  return products.reduce((total, product) => {
    return total + (product.stock * product.costo)
  }, 0)
}

export function calculateProfit(costo: number, precioVenta: number): number {
  return precioVenta - costo
}

export function calculateProfitMargin(costo: number, precioVenta: number): number {
  if (costo === 0) return 0
  return ((precioVenta - costo) / costo) * 100
}

// Búsquedas y filtros
export function getLowStockProducts(products: Product[], threshold: number): Product[] {
  return products.filter(product => product.stock <= threshold)
}

export function searchProductsByName(products: Product[], searchTerm: string): Product[] {
  const term = searchTerm.toLowerCase()
  return products.filter(product => 
    product.nombre.toLowerCase().includes(term)
  )
}

export function findClientByDNI(clients: Client[], dni: string): Client | undefined {
  return clients.find(client => client.dni === dni)
}