// test/lib/inventory-utils.test.ts
import {
  isValidDNI,
  isValidStock,
  isValidPrice,
  calculateTotalValue,
  calculateProfit,
  calculateProfitMargin,
  getLowStockProducts,
  searchProductsByName,
  findClientByDNI,
  type Product,
  type Client,
} from '@/lib/inventory-utils'

describe('Validaciones', () => {
  describe('isValidDNI', () => {
    it('retorna true para DNI válido de 8 dígitos', () => {
      expect(isValidDNI('12345678')).toBe(true)
      expect(isValidDNI('87654321')).toBe(true)
    })

    it('retorna false para DNI inválido', () => {
      expect(isValidDNI('1234567')).toBe(false) // 7 dígitos
      expect(isValidDNI('123456789')).toBe(false) // 9 dígitos
      expect(isValidDNI('1234567a')).toBe(false) // letras
      expect(isValidDNI('')).toBe(false) // vacío
    })
  })

  describe('isValidStock', () => {
    it('retorna true para stock válido', () => {
      expect(isValidStock(0)).toBe(true)
      expect(isValidStock(10)).toBe(true)
      expect(isValidStock(1000)).toBe(true)
    })

    it('retorna false para stock inválido', () => {
      expect(isValidStock(-1)).toBe(false) // negativo
      expect(isValidStock(3.5)).toBe(false) // decimal
      expect(isValidStock(NaN)).toBe(false) // NaN
    })
  })

  describe('isValidPrice', () => {
    it('retorna true para precio válido', () => {
      expect(isValidPrice(0)).toBe(true)
      expect(isValidPrice(10.99)).toBe(true)
      expect(isValidPrice(1000)).toBe(true)
    })

    it('retorna false para precio inválido', () => {
      expect(isValidPrice(-1)).toBe(false) // negativo
      expect(isValidPrice(NaN)).toBe(false) // NaN
    })
  })
})

describe('Cálculos', () => {
  describe('calculateTotalValue', () => {
    const mockProducts: Product[] = [
      { id_producto: 1, nombre: 'Producto A', stock: 10, costo: 100, precio_inicial: 150 },
      { id_producto: 2, nombre: 'Producto B', stock: 5, costo: 50, precio_inicial: 75 },
      { id_producto: 3, nombre: 'Producto C', stock: 20, costo: 25, precio_inicial: 40 },
    ]

    it('calcula el valor total del inventario correctamente', () => {
      // (10 * 100) + (5 * 50) + (20 * 25) = 1000 + 250 + 500 = 1750
      expect(calculateTotalValue(mockProducts)).toBe(1750)
    })

    it('retorna 0 para array vacío', () => {
      expect(calculateTotalValue([])).toBe(0)
    })

    it('maneja productos con stock 0', () => {
      const products: Product[] = [
        { id_producto: 1, nombre: 'Sin stock', stock: 0, costo: 100, precio_inicial: 150 },
      ]
      expect(calculateTotalValue(products)).toBe(0)
    })
  })

  describe('calculateProfit', () => {
    it('calcula la ganancia correctamente', () => {
      expect(calculateProfit(100, 150)).toBe(50)
      expect(calculateProfit(50, 75)).toBe(25)
      expect(calculateProfit(25, 40)).toBe(15)
    })

    it('maneja pérdidas (precio menor que costo)', () => {
      expect(calculateProfit(100, 80)).toBe(-20)
    })

    it('maneja precio igual al costo', () => {
      expect(calculateProfit(100, 100)).toBe(0)
    })
  })

  describe('calculateProfitMargin', () => {
    it('calcula el margen de ganancia correctamente', () => {
      expect(calculateProfitMargin(100, 150)).toBe(50) // 50% de ganancia
      expect(calculateProfitMargin(100, 200)).toBe(100) // 100% de ganancia
    })

    it('retorna 0 cuando el costo es 0', () => {
      expect(calculateProfitMargin(0, 100)).toBe(0)
    })

    it('maneja márgenes negativos', () => {
      expect(calculateProfitMargin(100, 80)).toBe(-20) // -20% (pérdida)
    })
  })
})

describe('Búsquedas y Filtros', () => {
  const mockProducts: Product[] = [
    { id_producto: 1, nombre: 'Camisa Roja', stock: 5, costo: 50, precio_inicial: 80 },
    { id_producto: 2, nombre: 'Pantalón Azul', stock: 15, costo: 80, precio_inicial: 120 },
    { id_producto: 3, nombre: 'Zapatos Negros', stock: 3, costo: 100, precio_inicial: 150 },
    { id_producto: 4, nombre: 'Camisa Blanca', stock: 2, costo: 50, precio_inicial: 80 },
  ]

  const mockClients: Client[] = [
    { id_cliente: 1, nombre: 'Juan Pérez', dni: '12345678', direccion: 'Av. Lima 123', telefono: '987654321' },
    { id_cliente: 2, nombre: 'María García', dni: '87654321', direccion: 'Jr. Arequipa 456', telefono: '912345678' },
    { id_cliente: 3, nombre: 'Carlos López', dni: '11223344', direccion: 'Calle Real 789', telefono: '923456789' },
  ]

  describe('getLowStockProducts', () => {
    it('retorna productos con stock bajo o igual al umbral', () => {
      const lowStock = getLowStockProducts(mockProducts, 5)
      expect(lowStock).toHaveLength(3)
      expect(lowStock[0].nombre).toBe('Camisa Roja')
      expect(lowStock[1].nombre).toBe('Zapatos Negros')
      expect(lowStock[2].nombre).toBe('Camisa Blanca')
    })

    it('retorna array vacío cuando no hay productos con stock bajo', () => {
      const lowStock = getLowStockProducts(mockProducts, 1)
      expect(lowStock).toHaveLength(0)
    })

    it('incluye productos con stock exactamente igual al umbral', () => {
      const lowStock = getLowStockProducts(mockProducts, 3)
      expect(lowStock).toHaveLength(2)
    })
  })

  describe('searchProductsByName', () => {
    it('encuentra productos por nombre (case insensitive)', () => {
      const results = searchProductsByName(mockProducts, 'camisa')
      expect(results).toHaveLength(2)
      expect(results[0].nombre).toBe('Camisa Roja')
      expect(results[1].nombre).toBe('Camisa Blanca')
    })

    it('encuentra productos con búsqueda parcial', () => {
      const results = searchProductsByName(mockProducts, 'za')
      expect(results).toHaveLength(1)
      expect(results[0].nombre).toBe('Zapatos Negros')
    })

    it('retorna array vacío cuando no encuentra coincidencias', () => {
      const results = searchProductsByName(mockProducts, 'inexistente')
      expect(results).toHaveLength(0)
    })

    it('retorna todos los productos con búsqueda vacía', () => {
      const results = searchProductsByName(mockProducts, '')
      expect(results).toHaveLength(4)
    })
  })

  describe('findClientByDNI', () => {
    it('encuentra cliente por DNI exacto', () => {
      const client = findClientByDNI(mockClients, '12345678')
      expect(client).toBeDefined()
      expect(client?.nombre).toBe('Juan Pérez')
    })

    it('retorna undefined cuando no encuentra el cliente', () => {
      const client = findClientByDNI(mockClients, '99999999')
      expect(client).toBeUndefined()
    })

    it('encuentra diferentes clientes correctamente', () => {
      const client1 = findClientByDNI(mockClients, '87654321')
      const client2 = findClientByDNI(mockClients, '11223344')
      
      expect(client1?.nombre).toBe('María García')
      expect(client2?.nombre).toBe('Carlos López')
    })
  })
})

describe('Casos extremos', () => {
  it('maneja arrays vacíos correctamente', () => {
    expect(calculateTotalValue([])).toBe(0)
    expect(getLowStockProducts([], 10)).toEqual([])
    expect(searchProductsByName([], 'test')).toEqual([])
    expect(findClientByDNI([], '12345678')).toBeUndefined()
  })

  it('maneja valores numéricos extremos', () => {
    expect(isValidPrice(0)).toBe(true)
    expect(isValidStock(0)).toBe(true)
    expect(calculateProfit(0, 0)).toBe(0)
  })
})