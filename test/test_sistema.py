import pytest
import os
import sys
from unittest.mock import patch, MagicMock, call
from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar las clases necesarias
from db import Base, Cliente, Producto, Amortizacion, NotaVenta, DetalleNotaVenta


class TestSistemaFunctions:
    """Suite de tests para las funciones del archivo sistema.py"""
    
    @pytest.fixture(scope="function")
    def test_session(self):
        """Fixture para crear una sesión de test"""
        test_engine = create_engine("sqlite:///:memory:")
        TestSession = sessionmaker(bind=test_engine)
        Base.metadata.create_all(test_engine)
        
        session = TestSession()
        yield session
        session.close()
    
    @pytest.fixture
    def mock_sistema_session(self, test_session):
        """Mock de la sesión de sistema.py"""
        with patch('sistema.session', test_session) as mock_session:
            yield mock_session
    
    @pytest.fixture
    def sample_cliente_data(self):
        """Datos de ejemplo para cliente"""
        return {
            "nombre": "Juan Pérez",
            "direccion": "Av. Lima 123",
            "telefono": "987654321",
            "dni": "12345678"
        }
    
    @pytest.fixture
    def sample_producto_data(self):
        """Datos de ejemplo para producto"""
        return {
            "nombre": "Producto Test",
            "stock": 100,
            "costo": Decimal("15.50"),
            "precio_inicial": Decimal("20.00")
        }

    @patch('sistema.messagebox')
    def test_agregar_cliente_exitoso(self, mock_messagebox, mock_sistema_session, sample_cliente_data):
        """Test para agregar cliente exitosamente"""
        from sistema import agregar_cliente
        
        agregar_cliente(**sample_cliente_data)
        
        # Verificar que se creó el cliente
        cliente = mock_sistema_session.query(Cliente).filter_by(dni="12345678").first()
        assert cliente is not None
        assert cliente.nombre == "Juan Pérez"
        assert cliente.telefono == "987654321"
        
        # Verificar que se mostró mensaje de éxito
        mock_messagebox.showinfo.assert_called_once()
        assert "creado exitosamente" in mock_messagebox.showinfo.call_args[0][1]
    
    @patch('sistema.messagebox')
    def test_agregar_cliente_campos_obligatorios(self, mock_messagebox, mock_sistema_session):
        """Test para validar campos obligatorios en agregar_cliente"""
        from sistema import agregar_cliente
        
        # Test sin nombre
        agregar_cliente(nombre="", direccion="Test", telefono="123", dni="12345678")
        mock_messagebox.showerror.assert_called()
        assert "obligatorios" in mock_messagebox.showerror.call_args[0][1]
        
        # Reset mock
        mock_messagebox.reset_mock()
        
        # Test sin DNI
        agregar_cliente(nombre="Juan", direccion="Test", telefono="123", dni="")
        mock_messagebox.showerror.assert_called()
        assert "obligatorios" in mock_messagebox.showerror.call_args[0][1]
    
    @patch('sistema.messagebox')
    def test_agregar_cliente_duplicado(self, mock_messagebox, mock_sistema_session, sample_cliente_data):
        """Test para verificar validación de cliente duplicado"""
        from sistema import agregar_cliente
        
        # Crear cliente inicial
        cliente_existente = Cliente(**sample_cliente_data)
        mock_sistema_session.add(cliente_existente)
        mock_sistema_session.commit()
        
        # Intentar crear cliente duplicado
        agregar_cliente(**sample_cliente_data)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "ya existe" in mock_messagebox.showerror.call_args[0][1]
    
    @patch('sistema.messagebox')
    def test_agregar_producto_exitoso(self, mock_messagebox, mock_sistema_session, sample_producto_data):
        """Test para agregar producto exitosamente"""
        from sistema import agregar_producto
        
        agregar_producto(**sample_producto_data)
        
        # Verificar que se creó el producto
        producto = mock_sistema_session.query(Producto).filter_by(nombre="Producto Test").first()
        assert producto is not None
        assert producto.stock == 100
        assert producto.costo == Decimal("15.50")
        
        # Verificar mensaje de éxito
        mock_messagebox.showinfo.assert_called_once()
        assert "creado exitosamente" in mock_messagebox.showinfo.call_args[0][1]
    
    @patch('sistema.messagebox')
    def test_agregar_producto_campos_obligatorios(self, mock_messagebox, mock_sistema_session):
        """Test para validar campos obligatorios en agregar_producto"""
        from sistema import agregar_producto
        
        # Test sin nombre
        agregar_producto(nombre="", stock=10, costo=Decimal("15.00"))
        mock_messagebox.showerror.assert_called()
        assert "obligatorios" in mock_messagebox.showerror.call_args[0][1]
        
        # Reset mock
        mock_messagebox.reset_mock()
        
        # Test sin stock
        agregar_producto(nombre="Test", stock=None, costo=Decimal("15.00"))
        mock_messagebox.showerror.assert_called()
    
    @patch('sistema.messagebox')
    def test_agregar_producto_duplicado(self, mock_messagebox, mock_sistema_session, sample_producto_data):
        """Test para verificar validación de producto duplicado"""
        from sistema import agregar_producto
        
        # Crear producto inicial
        producto_existente = Producto(**sample_producto_data)
        mock_sistema_session.add(producto_existente)
        mock_sistema_session.commit()
        
        # Intentar crear producto duplicado
        agregar_producto(**sample_producto_data)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "ya existe" in mock_messagebox.showerror.call_args[0][1]
    
    @patch('sistema.messagebox')
    def test_obtener_todos_los_clientes(self, mock_messagebox, mock_sistema_session):
        """Test para obtener todos los clientes"""
        from sistema import obtener_todos_los_clientes
        
        # Crear clientes de prueba
        cliente1 = Cliente(nombre="Cliente 1", dni="111", direccion="Dir 1", telefono="111")
        cliente2 = Cliente(nombre="Cliente 2", dni="222", direccion="Dir 2", telefono="222")
        mock_sistema_session.add_all([cliente1, cliente2])
        mock_sistema_session.commit()
        
        # Obtener clientes
        clientes = obtener_todos_los_clientes()
        
        assert len(clientes) == 2
        assert clientes[0].nombre in ["Cliente 1", "Cliente 2"]
        assert clientes[1].nombre in ["Cliente 1", "Cliente 2"]
    
    @patch('sistema.messagebox')
    def test_obtener_todos_los_productos(self, mock_messagebox, mock_sistema_session):
        """Test para obtener todos los productos ordenados"""
        from sistema import obtener_todos_los_productos
        
        # Crear productos de prueba
        producto1 = Producto(nombre="Producto A", stock=10, costo=Decimal("10.00"))
        producto2 = Producto(nombre="Producto B", stock=20, costo=Decimal("20.00"))
        mock_sistema_session.add_all([producto1, producto2])
        mock_sistema_session.commit()
        
        # Obtener productos
        productos = obtener_todos_los_productos()
        
        assert len(productos) == 2
        # Verificar que están ordenados por id_producto
        assert productos[0].id_producto <= productos[1].id_producto
    
    @patch('sistema.messagebox')
    def test_obtener_todos_los_productos_1(self, mock_messagebox, mock_sistema_session):
        """Test para obtener_todos_los_productos_1 con manejo de errores"""
        from sistema import obtener_todos_los_productos_1
        
        # Crear productos de prueba
        producto = Producto(nombre="Producto Test", stock=10, costo=Decimal("10.00"))
        mock_sistema_session.add(producto)
        mock_sistema_session.commit()
        
        # Obtener productos
        productos = obtener_todos_los_productos_1()
        
        assert len(productos) == 1
        assert productos[0].nombre == "Producto Test"
    
    @patch('sistema.messagebox')
    def test_obtener_todas_las_notas(self, mock_messagebox, mock_sistema_session):
        """Test para obtener todas las notas ordenadas"""
        from sistema import obtener_todas_las_notas
        
        # Crear cliente y notas de prueba
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota1 = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                         total=Decimal("100"), estado="Pendiente", fecha_venta=date.today())
        nota2 = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                         total=Decimal("200"), estado="Pagado", fecha_venta=date.today())
        mock_sistema_session.add_all([nota1, nota2])
        mock_sistema_session.commit()
        
        # Obtener notas
        notas = obtener_todas_las_notas()
        
        assert len(notas) == 2
        # Verificar ordenamiento ascendente
        assert notas[0].id_nota <= notas[1].id_nota
    
    @patch('sistema.messagebox')
    def test_obtener_notas_paginadas_sin_filtro(self, mock_messagebox, mock_sistema_session):
        """Test para obtener notas paginadas sin filtros"""
        from sistema import obtener_notas_paginadas
        
        # Crear cliente y notas de prueba
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        # Crear varias notas
        for i in range(5):
            nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                           total=Decimal(str(100 + i)), estado="Pendiente", fecha_venta=date.today())
            mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Obtener notas paginadas
        notas, total = obtener_notas_paginadas(page=1, per_page=3)
        
        assert len(notas) <= 3
        assert total == 5
    
    @patch('sistema.messagebox')
    def test_obtener_notas_paginadas_con_filtro_texto(self, mock_messagebox, mock_sistema_session):
        """Test para obtener notas paginadas con filtro de texto"""
        from sistema import obtener_notas_paginadas
        
        # Crear clientes con nombres diferentes
        cliente1 = Cliente(nombre="Juan Pérez", dni="111", direccion="Test", telefono="111")
        cliente2 = Cliente(nombre="María García", dni="222", direccion="Test", telefono="222")
        mock_sistema_session.add_all([cliente1, cliente2])
        mock_sistema_session.commit()
        
        # Crear notas para cada cliente
        nota1 = NotaVenta(id_cliente=cliente1.id_cliente, fecha=date.today(), 
                         total=Decimal("100"), estado="Pendiente", fecha_venta=date.today())
        nota2 = NotaVenta(id_cliente=cliente2.id_cliente, fecha=date.today(), 
                         total=Decimal("200"), estado="Pagado", fecha_venta=date.today())
        mock_sistema_session.add_all([nota1, nota2])
        mock_sistema_session.commit()
        
        # Filtrar por nombre de cliente
        notas, total = obtener_notas_paginadas(filtro_texto="Juan")
        
        assert len(notas) == 1
        assert total == 1
        assert notas[0].cliente.nombre == "Juan Pérez"
    
    @patch('sistema.messagebox')
    def test_obtener_notas_paginadas_con_filtro_estado_pedido(self, mock_messagebox, mock_sistema_session):
        """Test para obtener notas paginadas con filtro de estado_pedido"""
        from sistema import obtener_notas_paginadas
        
        # Crear cliente y notas con diferentes estados
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota1 = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                         total=Decimal("100"), estado="Pendiente", fecha_venta=date.today(),
                         estado_pedido="ABIERTO")
        nota2 = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                         total=Decimal("200"), estado="Pagado", fecha_venta=date.today(),
                         estado_pedido="CERRADO")
        mock_sistema_session.add_all([nota1, nota2])
        mock_sistema_session.commit()
        
        # Filtrar por estado_pedido
        notas, total = obtener_notas_paginadas(filtro_estado_pedido="ABIERTO")
        
        assert len(notas) == 1
        assert total == 1
        assert notas[0].estado_pedido == "ABIERTO"
    
    @patch('sistema.messagebox')
    def test_eliminar_cliente_exitoso(self, mock_messagebox, mock_sistema_session):
        """Test para eliminar cliente exitosamente"""
        from sistema import eliminar_cliente
        
        # Crear cliente de prueba
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        cliente_id = cliente.id_cliente
        
        # Mock de tabla y item
        mock_tabla = MagicMock()
        mock_item = "test_item"
        
        # Eliminar cliente
        eliminar_cliente(cliente_id, mock_tabla, mock_item)
        
        # Verificar que se eliminó
        cliente_eliminado = mock_sistema_session.query(Cliente).filter_by(id_cliente=cliente_id).first()
        assert cliente_eliminado is None
        
        # Verificar que se eliminó de la tabla gráfica
        mock_tabla.delete.assert_called_once_with(mock_item)
        
        # Verificar mensaje de éxito
        mock_messagebox.showinfo.assert_called_once()
        assert "eliminado correctamente" in mock_messagebox.showinfo.call_args[0][1]
    
    @patch('sistema.messagebox')
    def test_eliminar_cliente_no_existe(self, mock_messagebox, mock_sistema_session):
        """Test para eliminar cliente que no existe"""
        from sistema import eliminar_cliente
        
        mock_tabla = MagicMock()
        mock_item = "test_item"
        
        # Intentar eliminar cliente inexistente
        eliminar_cliente(999, mock_tabla, mock_item)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "no encontrado" in mock_messagebox.showerror.call_args[0][1]
    
    def test_crear_nota_venta_exitosa(self, mock_sistema_session):
        """Test para crear nota de venta exitosamente"""
        from sistema import crear_nota_venta
        
        # Crear cliente y producto de prueba
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        # Datos de productos para la nota
        productos_cantidades = [
            (producto.id_producto, 2, Decimal("15.00"), "M", "Rojo")
        ]
        
        # Crear nota de venta
        id_nota, total = crear_nota_venta(cliente.id_cliente, productos_cantidades, "Observación test")
        
        # Verificar que se creó la nota
        nota = mock_sistema_session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        assert nota is not None
        assert nota.total == Decimal("30.00")  # 2 * 15.00
        assert nota.observaciones == "Observación test"
        assert nota.estado_pedido == "ABIERTO"
        
        # Verificar que se creó el detalle
        detalle = mock_sistema_session.query(DetalleNotaVenta).filter_by(id_nota=id_nota).first()
        assert detalle is not None
        assert detalle.cantidad == 2
        assert detalle.precio_unitario == Decimal("15.00")
        assert detalle.talla == "M"
        assert detalle.color == "Rojo"
        assert detalle.subtotal == Decimal("30.00")
    
    def test_crear_nota_venta_cliente_inexistente(self, mock_sistema_session):
        """Test para crear nota de venta con cliente inexistente"""
        from sistema import crear_nota_venta
        
        productos_cantidades = [(1, 2, Decimal("15.00"), "M", "Rojo")]
        
        # Intentar crear nota con cliente inexistente
        with pytest.raises(ValueError) as exc_info:
            crear_nota_venta(999, productos_cantidades)
        
        assert "no existe" in str(exc_info.value)
    
    def test_crear_nota_venta_producto_inexistente(self, mock_sistema_session):
        """Test para crear nota de venta con producto inexistente"""
        from sistema import crear_nota_venta
        
        # Crear solo cliente
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        productos_cantidades = [(999, 2, Decimal("15.00"), "M", "Rojo")]
        
        # Intentar crear nota con producto inexistente
        with pytest.raises(ValueError) as exc_info:
            crear_nota_venta(cliente.id_cliente, productos_cantidades)
        
        assert "no existe" in str(exc_info.value)
    
    def test_crear_nota_venta_stock_insuficiente(self, mock_sistema_session):
        """Test para crear nota de venta con stock insuficiente"""
        from sistema import crear_nota_venta
        
        # Crear cliente y producto con poco stock
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=1, costo=Decimal("10.00"))  # Solo 1 en stock
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        productos_cantidades = [(producto.id_producto, 5, Decimal("15.00"), "M", "Rojo")]  # Pedir 5
        
        # Intentar crear nota con más cantidad que stock
        with pytest.raises(ValueError) as exc_info:
            crear_nota_venta(cliente.id_cliente, productos_cantidades)
        
        assert "stock" in str(exc_info.value).lower()
    
    def test_obtener_producto_por_id(self, mock_sistema_session):
        """Test para obtener producto por ID"""
        from sistema import obtener_producto_por_id
        
        # Crear producto de prueba
        producto = Producto(nombre="Producto Test", stock=10, costo=Decimal("15.00"))
        mock_sistema_session.add(producto)
        mock_sistema_session.commit()
        
        # Obtener producto
        producto_obtenido = obtener_producto_por_id(producto.id_producto)
        
        assert producto_obtenido is not None
        assert producto_obtenido.nombre == "Producto Test"
        
        # Test con ID inexistente
        producto_inexistente = obtener_producto_por_id(999)
        assert producto_inexistente is None
    
    def test_obtener_cliente_por_id(self, mock_sistema_session):
        """Test para obtener cliente por ID"""
        from sistema import obtener_cliente_por_id
        
        # Crear cliente de prueba
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        # Obtener cliente
        cliente_obtenido = obtener_cliente_por_id(cliente.id_cliente)
        
        assert cliente_obtenido is not None
        assert cliente_obtenido.nombre == "Cliente Test"
        
        # Test con ID inexistente
        cliente_inexistente = obtener_cliente_por_id(999)
        assert cliente_inexistente is None
    
    def test_obtener_productos_paginados(self, mock_sistema_session):
        """Test para obtener productos paginados con filtros"""
        from sistema import obtener_productos_paginados
        
        # Crear productos de prueba
        producto1 = Producto(nombre="Camisa Azul", stock=10, costo=Decimal("25.00"))
        producto2 = Producto(nombre="Pantalón Negro", stock=0, costo=Decimal("45.00"))  # Sin stock
        producto3 = Producto(nombre="Zapatos Rojos", stock=5, costo=Decimal("80.00"))
        mock_sistema_session.add_all([producto1, producto2, producto3])
        mock_sistema_session.commit()
        
        # Test sin filtros
        productos, total = obtener_productos_paginados()
        assert len(productos) >= 3
        assert total >= 3
        
        # Test con filtro de texto
        productos, total = obtener_productos_paginados(filtro_texto="Camisa")
        assert len(productos) == 1
        assert productos[0].nombre == "Camisa Azul"
        
        # Test solo con stock
        productos, total = obtener_productos_paginados(solo_stock=True)
        assert len(productos) == 2  # Camisa y Zapatos (producto2 tiene stock 0)
        for producto in productos:
            assert producto.stock > 0
    
    def test_obtener_detalles_nota_por_id_nota(self, mock_sistema_session):
        """Test para obtener detalles de nota por ID"""
        from sistema import obtener_detalles_nota_por_id_nota
        
        # Crear cliente, producto y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=10, costo=Decimal("15.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Crear detalles
        detalle1 = DetalleNotaVenta(id_nota=nota.id_nota, id_producto=producto.id_producto,
                                   cantidad=2, precio_unitario=Decimal("15.00"), 
                                   talla="M", color="Rojo", subtotal=Decimal("30.00"))
        mock_sistema_session.add(detalle1)
        mock_sistema_session.commit()
        
        # Obtener detalles
        detalles = obtener_detalles_nota_por_id_nota(nota.id_nota)
        
        assert len(detalles) == 1
        assert detalles[0].cantidad == 2
        assert detalles[0].color == "Rojo"
    
    def test_obtener_nota_venta_por_id(self, mock_sistema_session):
        """Test para obtener nota de venta por ID"""
        from sistema import obtener_nota_venta_por_id
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Obtener nota
        nota_obtenida = obtener_nota_venta_por_id(nota.id_nota)
        
        assert nota_obtenida is not None
        assert nota_obtenida.total == Decimal("100.00")
        
        # Test con ID inexistente
        nota_inexistente = obtener_nota_venta_por_id(999)
        assert nota_inexistente is None
    
    def test_agregar_amortizacion_exitosa(self, mock_sistema_session):
        """Test para agregar amortización exitosamente"""
        from sistema import agregar_amortizacion
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Agregar amortización
        agregar_amortizacion(nota.id_nota, Decimal("50.00"))
        
        # Verificar que se creó
        amortizacion = mock_sistema_session.query(Amortizacion).filter_by(id_nota=nota.id_nota).first()
        assert amortizacion is not None
        assert amortizacion.monto == Decimal("50.00")
    
    def test_eliminar_amortizacion_exitosa(self, mock_sistema_session):
        """Test para eliminar amortización exitosamente"""
        from sistema import eliminar_amortizacion
        
        # Crear cliente, nota y amortización
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        amortizacion = Amortizacion(id_nota=nota.id_nota, monto=Decimal("50.00"), fecha=date.today())
        mock_sistema_session.add(amortizacion)
        mock_sistema_session.commit()
        amortizacion_id = amortizacion.id_amortizacion
        
        # Eliminar amortización
        eliminar_amortizacion(amortizacion_id)
        
        # Verificar que se eliminó
        amortizacion_eliminada = mock_sistema_session.query(Amortizacion).filter_by(
            id_amortizacion=amortizacion_id).first()
        assert amortizacion_eliminada is None
    
    def test_eliminar_amortizacion_inexistente(self, mock_sistema_session):
        """Test para eliminar amortización inexistente"""
        from sistema import eliminar_amortizacion
        
        # Intentar eliminar amortización inexistente
        with pytest.raises(ValueError) as exc_info:
            eliminar_amortizacion(999)
        
        assert "no existe" in str(exc_info.value)

    @patch('sistema.messagebox')
    def test_manejo_errores_obtener_clientes(self, mock_messagebox, mock_sistema_session):
        """Test para manejo de errores en obtener_todos_los_clientes"""
        from sistema import obtener_todos_los_clientes
        
        # Simular error en la consulta
        with patch.object(mock_sistema_session, 'query', side_effect=Exception("Database error")):
            clientes = obtener_todos_los_clientes()
            
            assert clientes == []
            mock_messagebox.showerror.assert_called_once()
            assert "Error al obtener los clientes" in mock_messagebox.showerror.call_args[0][1]

    def test_eliminar_amortizacion_inexistente(self, mock_sistema_session):
        """Test para eliminar amortización inexistente"""
        from sistema import eliminar_amortizacion
        
        # Intentar eliminar amortización inexistente
        with pytest.raises(ValueError) as exc_info:
            eliminar_amortizacion(999)
        
        assert "no existe" in str(exc_info.value)

    def test_obtener_amortizaciones_por_id_nota(self, mock_sistema_session):
        """Test para obtener amortizaciones por ID de nota"""
        from sistema import obtener_amortizaciones_por_id_nota
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Crear varias amortizaciones
        amortizacion1 = Amortizacion(id_nota=nota.id_nota, monto=Decimal("30.00"), fecha=date.today())
        amortizacion2 = Amortizacion(id_nota=nota.id_nota, monto=Decimal("20.00"), fecha=date.today())
        mock_sistema_session.add_all([amortizacion1, amortizacion2])
        mock_sistema_session.commit()
        
        # Obtener amortizaciones
        amortizaciones = obtener_amortizaciones_por_id_nota(nota.id_nota)
        
        assert len(amortizaciones) == 2
        montos = [amor.monto for amor in amortizaciones]
        assert Decimal("30.00") in montos
        assert Decimal("20.00") in montos


    @patch('sistema.messagebox')
    def test_agregar_venta_nota_inexistente(self, mock_messagebox, mock_sistema_session):
        """Test para confirmar venta con nota inexistente"""
        from sistema import agregar_venta
        
        # Intentar confirmar venta con nota inexistente
        agregar_venta(999)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "no existe" in mock_messagebox.showerror.call_args[0][1] or "Nota_Venta" in mock_messagebox.showerror.call_args[0][1]

    @patch('sistema.messagebox')
    def test_agregar_venta_producto_inexistente(self, mock_messagebox, mock_sistema_session):
        """Test para confirmar venta con producto inexistente en detalle"""
        from sistema import agregar_venta
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Crear detalle con producto inexistente
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=999,  # ID inexistente
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Intentar confirmar venta
        agregar_venta(nota.id_nota)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "no existe" in mock_messagebox.showerror.call_args[0][1]

    @patch('sistema.messagebox')
    def test_agregar_venta_stock_insuficiente(self, mock_messagebox, mock_sistema_session):
        """Test para confirmar venta con stock insuficiente"""
        from sistema import agregar_venta
        
        # Crear cliente, producto con poco stock
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=1, costo=Decimal("10.00"))  # Solo 1 en stock
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Crear detalle que requiere más stock del disponible
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=5, precio_unitario=Decimal("15.00"),  # Requiere 5, solo hay 1
            talla="M", color="Rojo", subtotal=Decimal("75.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Intentar confirmar venta
        agregar_venta(nota.id_nota)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        error_message = mock_messagebox.showerror.call_args[0][1]
        assert "stock" in error_message.lower()

    @patch('sistema.messagebox')
    def test_modificar_producto_exitoso(self, mock_messagebox, mock_sistema_session):
        """Test para modificar producto exitosamente"""
        from sistema import modificar_producto
        
        # Crear producto inicial
        producto = Producto(nombre="Producto Original", stock=10, costo=Decimal("15.00"))
        mock_sistema_session.add(producto)
        mock_sistema_session.commit()
        producto_id = producto.id_producto
        
        # Modificar producto
        modificar_producto(
            producto_id, "Producto Modificado", 20, 
            Decimal("25.00"), Decimal("35.00")
        )
        
        # Verificar que se modificó
        producto_modificado = mock_sistema_session.query(Producto).filter_by(id_producto=producto_id).first()
        assert producto_modificado.nombre == "Producto Modificado"
        assert producto_modificado.stock == 20
        assert producto_modificado.costo == Decimal("25.00")
        assert producto_modificado.precio_inicial == Decimal("35.00")
        
        # Verificar mensaje de éxito
        mock_messagebox.showinfo.assert_called_once()
        assert "modificado exitosamente" in mock_messagebox.showinfo.call_args[0][1]

    @patch('sistema.messagebox')
    def test_modificar_producto_inexistente(self, mock_messagebox, mock_sistema_session):
        """Test para modificar producto inexistente"""
        from sistema import modificar_producto
        
        # Intentar modificar producto inexistente
        modificar_producto(999, "Producto Inexistente", 10, Decimal("15.00"))
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "no existe" in mock_messagebox.showerror.call_args[0][1]

    @patch('sistema.messagebox')
    def test_eliminar_producto_exitoso(self, mock_messagebox, mock_sistema_session):
        """Test para eliminar producto exitosamente"""
        from sistema import eliminar_producto
        
        # Crear producto
        producto = Producto(nombre="Producto a Eliminar", stock=10, costo=Decimal("15.00"))
        mock_sistema_session.add(producto)
        mock_sistema_session.commit()
        producto_id = producto.id_producto
        
        # Eliminar producto
        eliminar_producto(producto_id)
        
        # Verificar que se eliminó
        producto_eliminado = mock_sistema_session.query(Producto).filter_by(id_producto=producto_id).first()
        assert producto_eliminado is None
        
        # Verificar mensaje de éxito
        mock_messagebox.showinfo.assert_called_once()
        assert "eliminado exitosamente" in mock_messagebox.showinfo.call_args[0][1]

    @patch('sistema.messagebox')
    def test_eliminar_producto_inexistente(self, mock_messagebox, mock_sistema_session):
        """Test para eliminar producto inexistente"""
        from sistema import eliminar_producto
        
        # Intentar eliminar producto inexistente
        eliminar_producto(999)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "no existe" in mock_messagebox.showerror.call_args[0][1]

    @patch('sistema.messagebox')
    def test_obtener_costo_total_inventario_con_productos(self, mock_messagebox, mock_sistema_session):
        """Test para calcular costo total del inventario con productos"""
        from sistema import obtener_costo_total_inventario
        
        # Crear productos con diferentes costos y stocks
        producto1 = Producto(nombre="Producto 1", stock=10, costo=Decimal("15.00"))  # 10 * 15 = 150
        producto2 = Producto(nombre="Producto 2", stock=5, costo=Decimal("20.00"))   # 5 * 20 = 100
        mock_sistema_session.add_all([producto1, producto2])
        mock_sistema_session.commit()
        
        # Calcular costo total
        costo_total = obtener_costo_total_inventario()
        
        # Verificar resultado (150 + 100 = 250)
        assert costo_total == Decimal("250.00")

    @patch('sistema.messagebox')
    def test_obtener_costo_total_inventario_sin_productos(self, mock_messagebox, mock_sistema_session):
        """Test para calcular costo total del inventario sin productos"""
        from sistema import obtener_costo_total_inventario
        
        # No crear productos
        costo_total = obtener_costo_total_inventario()
        
        # Verificar que retorna 0
        assert costo_total == 0

    @patch('sistema.messagebox')
    def test_modificar_cliente_exitoso(self, mock_messagebox, mock_sistema_session):
        """Test para modificar cliente exitosamente"""
        from sistema import modificar_cliente
        
        # Crear cliente inicial
        cliente = Cliente(nombre="Cliente Original", dni="111", direccion="Dir Original", telefono="111")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        cliente_id = cliente.id_cliente
        
        # Modificar cliente
        modificar_cliente(
            cliente_id, "Cliente Modificado", "Dir Modificada", 
            "222", "222"
        )
        
        # Verificar que se modificó
        cliente_modificado = mock_sistema_session.query(Cliente).filter_by(id_cliente=cliente_id).first()
        assert cliente_modificado.nombre == "Cliente Modificado"
        assert cliente_modificado.direccion == "Dir Modificada"
        assert cliente_modificado.telefono == "222"
        assert cliente_modificado.dni == "222"
        
        # Verificar mensaje de éxito
        mock_messagebox.showinfo.assert_called_once()
        assert "modificado exitosamente" in mock_messagebox.showinfo.call_args[0][1]

    @patch('sistema.messagebox')
    def test_modificar_cliente_inexistente(self, mock_messagebox, mock_sistema_session):
        """Test para modificar cliente inexistente"""
        from sistema import modificar_cliente
        
        # Intentar modificar cliente inexistente
        modificar_cliente(999, "Cliente Inexistente", "Dirección", "123", "123")
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        assert "no existe" in mock_messagebox.showerror.call_args[0][1]

    @patch('sistema.messagebox')
    def test_eliminar_nota_venta_exitosa(self, mock_messagebox, mock_sistema_session):
        """Test para eliminar nota de venta exitosamente"""
        from sistema import eliminar_nota_venta
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        nota_id = nota.id_nota
        
        # Eliminar nota
        eliminar_nota_venta(nota_id)
        
        # Verificar que se eliminó
        nota_eliminada = mock_sistema_session.query(NotaVenta).filter_by(id_nota=nota_id).first()
        assert nota_eliminada is None
        
        # Verificar mensaje de éxito
        mock_messagebox.showinfo.assert_called_once()
        assert "eliminada exitosamente" in mock_messagebox.showinfo.call_args[0][1]

    @patch('sistema.messagebox')
    def test_eliminar_nota_venta_inexistente(self, mock_messagebox, mock_sistema_session):
        """Test para eliminar nota de venta inexistente"""
        from sistema import eliminar_nota_venta
        
        # Intentar eliminar nota inexistente
        eliminar_nota_venta(999)
        
        # Verificar mensaje de error
        mock_messagebox.showerror.assert_called()
        error_message = mock_messagebox.showerror.call_args[0][1]
        assert "no existe" in error_message or "Nota_Venta" in error_message

    @patch('sistema.messagebox')
    def test_manejo_errores_obtener_clientes(self, mock_messagebox, mock_sistema_session):
        """Test para manejo de errores en obtener_todos_los_clientes"""
        from sistema import obtener_todos_los_clientes
        
        # Simular error en la consulta
        with patch.object(mock_sistema_session, 'query', side_effect=Exception("Database error")):
            clientes = obtener_todos_los_clientes()
            
            assert clientes == []
            mock_messagebox.showerror.assert_called_once()
            assert "Error al obtener los clientes" in mock_messagebox.showerror.call_args[0][1]

    @patch('sistema.messagebox')
    def test_manejo_errores_obtener_productos_1(self, mock_messagebox, mock_sistema_session):
        """Test para manejo de errores en obtener_todos_los_productos_1"""
        from sistema import obtener_todos_los_productos_1
        
        # Simular error en la consulta
        with patch.object(mock_sistema_session, 'query', side_effect=Exception("Database error")):
            productos = obtener_todos_los_productos_1()
            
            assert productos == []
            mock_messagebox.showerror.assert_called_once()
            assert "Error al obtener los productos" in mock_messagebox.showerror.call_args[0][1]

    @patch('sistema.messagebox')
    def test_manejo_errores_obtener_costo_inventario(self, mock_messagebox, mock_sistema_session):
        """Test para manejo de errores en obtener_costo_total_inventario"""
        from sistema import obtener_costo_total_inventario
        
        # Simular error en la consulta
        with patch.object(mock_sistema_session, 'query', side_effect=Exception("Database error")):
            costo = obtener_costo_total_inventario()
            
            assert costo == 0
            mock_messagebox.showerror.assert_called_once()
            assert "Error al calcular el costo total" in mock_messagebox.showerror.call_args[0][1]

    def test_actualizar_observaciones_nota_exitoso(self, mock_sistema_session):
        """Test para actualizar observaciones de una nota exitosamente"""
        from sistema import actualizar_observaciones_nota
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today(),
                        observaciones="Observación inicial")
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Actualizar observaciones
        resultado = actualizar_observaciones_nota(nota.id_nota, "Nueva observación")
        
        # Verificar actualización
        assert resultado is True
        nota_actualizada = mock_sistema_session.query(NotaVenta).filter_by(id_nota=nota.id_nota).first()
        assert nota_actualizada.observaciones == "Nueva observación"

    def test_actualizar_observaciones_nota_inexistente(self, mock_sistema_session):
        """Test para actualizar observaciones de nota inexistente"""
        from sistema import actualizar_observaciones_nota
        
        # Intentar actualizar nota inexistente
        with pytest.raises(ValueError) as exc_info:
            actualizar_observaciones_nota(999, "Nueva observación")
        
        assert "no existe" in str(exc_info.value) or "Nota" in str(exc_info.value)

    def test_obtener_observaciones_nota_exitoso(self, mock_sistema_session):
        """Test para obtener observaciones de una nota"""
        from sistema import obtener_observaciones_nota
        
        # Crear cliente y nota con observaciones
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today(),
                        observaciones="Observación de prueba")
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Obtener observaciones
        observaciones = obtener_observaciones_nota(nota.id_nota)
        
        assert observaciones == "Observación de prueba"

    def test_obtener_observaciones_nota_inexistente(self, mock_sistema_session):
        """Test para obtener observaciones de nota inexistente"""
        from sistema import obtener_observaciones_nota
        
        # Intentar obtener observaciones de nota inexistente
        with pytest.raises(ValueError) as exc_info:
            obtener_observaciones_nota(999)
        
        assert "no existe" in str(exc_info.value) or "Nota" in str(exc_info.value)

    def test_actualizar_nota_venta_mejorada_actualizar_existente(self, mock_sistema_session):
        """Test para actualizar detalles existentes de una nota"""
        from sistema import actualizar_nota_venta_mejorada
        
        # Crear cliente, producto y nota con detalle
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Actualizar el detalle con nuevos datos
        nuevos_detalles = [
            (producto.id_producto, 5, Decimal("20.00"), "Azul", "L", Decimal("100.00"))
        ]
        productos_a_eliminar = []
        
        actualizar_nota_venta_mejorada(nota.id_nota, nuevos_detalles, productos_a_eliminar)
        
        # Verificar actualización
        detalle_actualizado = mock_sistema_session.query(DetalleNotaVenta).filter_by(
            id_nota=nota.id_nota, id_producto=producto.id_producto).first()
        assert detalle_actualizado.cantidad == 5
        assert detalle_actualizado.precio_unitario == Decimal("20.00")
        assert detalle_actualizado.color == "Azul"
        assert detalle_actualizado.talla == "L"
        
        # Verificar que se actualizó el total de la nota
        nota_actualizada = mock_sistema_session.query(NotaVenta).filter_by(id_nota=nota.id_nota).first()
        assert nota_actualizada.total == Decimal("100.00")

    def test_actualizar_nota_venta_mejorada_agregar_nuevo(self, mock_sistema_session):
        """Test para agregar nuevo detalle a una nota existente"""
        from sistema import actualizar_nota_venta_mejorada
        
        # Crear cliente, productos y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto1 = Producto(nombre="Producto 1", stock=100, costo=Decimal("10.00"))
        producto2 = Producto(nombre="Producto 2", stock=50, costo=Decimal("15.00"))
        mock_sistema_session.add_all([cliente, producto1, producto2])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle1 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto1.id_producto,
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        mock_sistema_session.add(detalle1)
        mock_sistema_session.commit()
        
        # Agregar nuevo producto y mantener el existente
        nuevos_detalles = [
            (producto1.id_producto, 2, Decimal("15.00"), "Rojo", "M", Decimal("30.00")),
            (producto2.id_producto, 3, Decimal("20.00"), "Verde", "S", Decimal("60.00"))  # Nuevo
        ]
        productos_a_eliminar = []
        
        actualizar_nota_venta_mejorada(nota.id_nota, nuevos_detalles, productos_a_eliminar)
        
        # Verificar que se agregó el nuevo detalle
        detalles = mock_sistema_session.query(DetalleNotaVenta).filter_by(id_nota=nota.id_nota).all()
        assert len(detalles) == 2
        
        # Verificar total actualizado (30 + 60 = 90)
        nota_actualizada = mock_sistema_session.query(NotaVenta).filter_by(id_nota=nota.id_nota).first()
        assert nota_actualizada.total == Decimal("90.00")

    def test_actualizar_nota_venta_mejorada_eliminar_producto(self, mock_sistema_session):
        """Test para eliminar productos específicos de una nota"""
        from sistema import actualizar_nota_venta_mejorada
        
        # Crear cliente, productos y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto1 = Producto(nombre="Producto 1", stock=100, costo=Decimal("10.00"))
        producto2 = Producto(nombre="Producto 2", stock=50, costo=Decimal("15.00"))
        mock_sistema_session.add_all([cliente, producto1, producto2])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("90.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle1 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto1.id_producto,
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        detalle2 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto2.id_producto,
            cantidad=3, precio_unitario=Decimal("20.00"), 
            talla="S", color="Verde", subtotal=Decimal("60.00")
        )
        mock_sistema_session.add_all([detalle1, detalle2])
        mock_sistema_session.commit()
        
        # Eliminar producto1, mantener producto2
        nuevos_detalles = [
            (producto2.id_producto, 3, Decimal("20.00"), "Verde", "S", Decimal("60.00"))
        ]
        productos_a_eliminar = [producto1.id_producto]
        
        actualizar_nota_venta_mejorada(nota.id_nota, nuevos_detalles, productos_a_eliminar)
        
        # Verificar que solo queda un detalle
        detalles = mock_sistema_session.query(DetalleNotaVenta).filter_by(id_nota=nota.id_nota).all()
        assert len(detalles) == 1
        assert detalles[0].id_producto == producto2.id_producto
        
        # Verificar total actualizado
        nota_actualizada = mock_sistema_session.query(NotaVenta).filter_by(id_nota=nota.id_nota).first()
        assert nota_actualizada.total == Decimal("60.00")

    def test_actualizar_detalle_producto_cantidad(self, mock_sistema_session):
        """Test para actualizar solo la cantidad de un detalle"""
        from sistema import actualizar_detalle_producto
        
        # Crear cliente, producto y nota con detalle
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Actualizar solo la cantidad
        actualizar_detalle_producto(nota.id_nota, producto.id_producto, cantidad=5)
        
        # Verificar actualización
        detalle_actualizado = mock_sistema_session.query(DetalleNotaVenta).filter_by(
            id_nota=nota.id_nota, id_producto=producto.id_producto).first()
        assert detalle_actualizado.cantidad == 5
        assert detalle_actualizado.subtotal == Decimal("75.00")  # 5 * 15
        
        # Verificar que otros campos no cambiaron
        assert detalle_actualizado.precio_unitario == Decimal("15.00")
        assert detalle_actualizado.color == "Rojo"
        assert detalle_actualizado.talla == "M"

    def test_actualizar_detalle_producto_precio(self, mock_sistema_session):
        """Test para actualizar solo el precio de un detalle"""
        from sistema import actualizar_detalle_producto
        
        # Crear cliente, producto y nota con detalle
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Actualizar solo el precio
        actualizar_detalle_producto(nota.id_nota, producto.id_producto, precio_unitario=Decimal("20.00"))
        
        # Verificar actualización
        detalle_actualizado = mock_sistema_session.query(DetalleNotaVenta).filter_by(
            id_nota=nota.id_nota, id_producto=producto.id_producto).first()
        assert detalle_actualizado.precio_unitario == Decimal("20.00")
        assert detalle_actualizado.subtotal == Decimal("40.00")  # 2 * 20

    def test_actualizar_detalle_producto_color_talla(self, mock_sistema_session):
        """Test para actualizar color y talla de un detalle"""
        from sistema import actualizar_detalle_producto
        
        # Crear cliente, producto y nota con detalle
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Actualizar color y talla
        actualizar_detalle_producto(nota.id_nota, producto.id_producto, color="Azul", talla="L")
        
        # Verificar actualización
        detalle_actualizado = mock_sistema_session.query(DetalleNotaVenta).filter_by(
            id_nota=nota.id_nota, id_producto=producto.id_producto).first()
        assert detalle_actualizado.color == "Azul"
        assert detalle_actualizado.talla == "L"

    def test_actualizar_detalle_producto_inexistente(self, mock_sistema_session):
        """Test para actualizar detalle inexistente"""
        from sistema import actualizar_detalle_producto
        
        # Intentar actualizar detalle inexistente
        with pytest.raises(ValueError) as exc_info:
            actualizar_detalle_producto(999, 999, cantidad=5)
        
        assert "No se encontró el detalle" in str(exc_info.value)

    def test_agregar_detalle_nota_exitoso(self, mock_sistema_session):
        """Test para agregar detalle a una nota exitosamente"""
        from sistema import agregar_detalle_nota
        
        # Crear cliente, producto y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("0.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Agregar detalle
        agregar_detalle_nota(
            nota.id_nota, producto.id_producto, 3, 
            Decimal("25.00"), "Negro", "XL", Decimal("75.00")
        )
        
        # Verificar que se agregó
        detalle = mock_sistema_session.query(DetalleNotaVenta).filter_by(
            id_nota=nota.id_nota, id_producto=producto.id_producto).first()
        assert detalle is not None
        assert detalle.cantidad == 3
        assert detalle.precio_unitario == Decimal("25.00")
        assert detalle.color == "Negro"
        assert detalle.talla == "XL"
        assert detalle.subtotal == Decimal("75.00")

    def test_eliminar_detalle_nota_exitoso(self, mock_sistema_session):
        """Test para eliminar detalle de una nota exitosamente"""
        from sistema import eliminar_detalle_nota
        
        # Crear cliente, producto y nota con detalle
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("30.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("15.00"), 
            talla="M", color="Rojo", subtotal=Decimal("30.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Eliminar detalle
        eliminar_detalle_nota(nota.id_nota, producto.id_producto)
        
        # Verificar que se eliminó
        detalle_eliminado = mock_sistema_session.query(DetalleNotaVenta).filter_by(
            id_nota=nota.id_nota, id_producto=producto.id_producto).first()
        assert detalle_eliminado is None
        
        # Verificar que se actualizó el total de la nota
        nota_actualizada = mock_sistema_session.query(NotaVenta).filter_by(id_nota=nota.id_nota).first()
        assert nota_actualizada.total == Decimal("0.00")  # 30 - 30

    def test_eliminar_detalle_nota_inexistente(self, mock_sistema_session):
        """Test para eliminar detalle inexistente"""
        from sistema import eliminar_detalle_nota
        
        # Crear cliente y nota sin detalles
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("0.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Intentar eliminar detalle inexistente
        with pytest.raises(ValueError) as exc_info:
            eliminar_detalle_nota(nota.id_nota, 999)
        
        assert "no existe" in str(exc_info.value)

    def test_eliminar_detalle_nota_sin_nota(self, mock_sistema_session):
        """Test para eliminar detalle cuando la nota no existe"""
        from sistema import eliminar_detalle_nota
        
        # Intentar eliminar detalle de nota inexistente
        with pytest.raises(ValueError) as exc_info:
            eliminar_detalle_nota(999, 999)
        
        assert "no existe" in str(exc_info.value) or "no se pudo eliminar" in str(exc_info.value).lower()

    def test_obtener_ventas_por_fecha(self, mock_sistema_session):
        """Test para obtener ventas canceladas por rango de fechas"""
        from sistema import obtener_ventas_por_fecha
        from datetime import timedelta
        
        # Crear cliente y productos
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        # Crear notas con diferentes estados y fechas
        fecha_hoy = date.today()
        fecha_ayer = fecha_hoy - timedelta(days=1)
        fecha_hace_5_dias = fecha_hoy - timedelta(days=5)
        
        # Nota cancelada dentro del rango
        nota1 = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_ayer, 
                         total=Decimal("100.00"), estado="Cancelado", fecha_venta=fecha_ayer)
        # Nota cancelada fuera del rango
        nota2 = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_hace_5_dias, 
                         total=Decimal("200.00"), estado="Cancelado", fecha_venta=fecha_hace_5_dias)
        # Nota pendiente (no cancelada)
        nota3 = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_hoy, 
                         total=Decimal("150.00"), estado="Pendiente", fecha_venta=fecha_hoy)
        mock_sistema_session.add_all([nota1, nota2, nota3])
        mock_sistema_session.commit()
        
        # Agregar detalles a las notas
        detalle1 = DetalleNotaVenta(
            id_nota=nota1.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("50.00"), 
            talla="M", color="Rojo", subtotal=Decimal("100.00")
        )
        mock_sistema_session.add(detalle1)
        mock_sistema_session.commit()
        
        # Obtener ventas de los últimos 3 días
        fecha_inicio = fecha_hoy - timedelta(days=3)
        fecha_fin = fecha_hoy
        
        ventas = obtener_ventas_por_fecha(fecha_inicio, fecha_fin)
        
        # Verificar que solo retorna la venta cancelada dentro del rango
        assert len(ventas) == 1
        assert ventas[0].id_nota == nota1.id_nota
        assert ventas[0].estado == "Cancelado"

    def test_calcular_ganancia(self, mock_sistema_session):
        """Test para calcular ganancia de ventas"""
        from sistema import calcular_ganancia
        
        # Crear cliente y productos
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto1 = Producto(nombre="Producto 1", stock=100, costo=Decimal("10.00"))
        producto2 = Producto(nombre="Producto 2", stock=50, costo=Decimal("15.00"))
        mock_sistema_session.add_all([cliente, producto1, producto2])
        mock_sistema_session.commit()
        
        # Crear nota cancelada
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("120.00"), estado="Cancelado", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Agregar detalles con ganancias
        # Producto 1: precio 25, costo 10, ganancia por unidad 15, cantidad 2 = ganancia 30
        detalle1 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto1.id_producto,
            cantidad=2, precio_unitario=Decimal("25.00"), 
            talla="M", color="Rojo", subtotal=Decimal("50.00")
        )
        # Producto 2: precio 35, costo 15, ganancia por unidad 20, cantidad 2 = ganancia 40
        detalle2 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto2.id_producto,
            cantidad=2, precio_unitario=Decimal("35.00"), 
            talla="L", color="Azul", subtotal=Decimal("70.00")
        )
        mock_sistema_session.add_all([detalle1, detalle2])
        mock_sistema_session.commit()
        
        # Calcular ganancia
        ventas = [nota]
        ganancia = calcular_ganancia(ventas)
        
        # Ganancia total: 30 + 40 = 70
        assert ganancia == Decimal("70.00")

    def test_calcular_ganancia_sin_ventas(self, mock_sistema_session):
        """Test para calcular ganancia sin ventas"""
        from sistema import calcular_ganancia
        
        # Calcular ganancia sin ventas
        ganancia = calcular_ganancia([])
        
        assert ganancia == 0
        
    def test_calcular_total(self, mock_sistema_session):
        """Test para calcular el total de ventas"""
        from sistema import calcular_total
        
        # Crear cliente y productos
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto1 = Producto(nombre="Producto 1", stock=100, costo=Decimal("10.00"))
        producto2 = Producto(nombre="Producto 2", stock=50, costo=Decimal("15.00"))
        mock_sistema_session.add_all([cliente, producto1, producto2])
        mock_sistema_session.commit()
        
        # Crear nota con detalles
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("120.00"), estado="Cancelado", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Detalles: 2 * 25 = 50, 3 * 30 = 90, total = 140
        detalle1 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto1.id_producto,
            cantidad=2, precio_unitario=Decimal("25.00"), 
            talla="M", color="Rojo", subtotal=Decimal("50.00")
        )
        detalle2 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto2.id_producto,
            cantidad=3, precio_unitario=Decimal("30.00"), 
            talla="L", color="Azul", subtotal=Decimal("90.00")
        )
        mock_sistema_session.add_all([detalle1, detalle2])
        mock_sistema_session.commit()
        
        # Calcular total
        ventas = [nota]
        total = calcular_total(ventas)
        
        assert total == Decimal("140.00")

    def test_calcular_total_sin_ventas(self, mock_sistema_session):
        """Test para calcular total sin ventas"""
        from sistema import calcular_total
        
        total = calcular_total([])
        assert total == 0

    def test_calcular_costo_total(self, mock_sistema_session):
        """Test para calcular el costo total de ventas"""
        from sistema import calcular_costo_total
        
        # Crear cliente y productos
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto1 = Producto(nombre="Producto 1", stock=100, costo=Decimal("10.00"))
        producto2 = Producto(nombre="Producto 2", stock=50, costo=Decimal("15.00"))
        mock_sistema_session.add_all([cliente, producto1, producto2])
        mock_sistema_session.commit()
        
        # Crear nota con detalles
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("120.00"), estado="Cancelado", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Costos: 2 * 10 = 20, 3 * 15 = 45, total costo = 65
        detalle1 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto1.id_producto,
            cantidad=2, precio_unitario=Decimal("25.00"), 
            talla="M", color="Rojo", subtotal=Decimal("50.00")
        )
        detalle2 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto2.id_producto,
            cantidad=3, precio_unitario=Decimal("30.00"), 
            talla="L", color="Azul", subtotal=Decimal("90.00")
        )
        mock_sistema_session.add_all([detalle1, detalle2])
        mock_sistema_session.commit()
        
        # Calcular costo total
        ventas = [nota]
        costo_total = calcular_costo_total(ventas)
        
        assert costo_total == Decimal("65.00")

    def test_calcular_costo_total_sin_ventas(self, mock_sistema_session):
        """Test para calcular costo total sin ventas"""
        from sistema import calcular_costo_total
        
        costo = calcular_costo_total([])
        assert costo == 0

    def test_obtener_productos_vendidos(self, mock_sistema_session):
        """Test para obtener lista detallada de productos vendidos"""
        from sistema import obtener_productos_vendidos
        
        # Crear cliente y productos
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto1 = Producto(nombre="Camisa Azul", stock=100, costo=Decimal("10.00"))
        producto2 = Producto(nombre="Pantalón Negro", stock=50, costo=Decimal("15.00"))
        mock_sistema_session.add_all([cliente, producto1, producto2])
        mock_sistema_session.commit()
        
        # Crear nota con detalles
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("120.00"), estado="Cancelado", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle1 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto1.id_producto,
            cantidad=2, precio_unitario=Decimal("25.00"), 
            talla="M", color="Rojo", subtotal=Decimal("50.00")
        )
        detalle2 = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto2.id_producto,
            cantidad=3, precio_unitario=Decimal("30.00"), 
            talla="L", color="Azul", subtotal=Decimal("90.00")
        )
        mock_sistema_session.add_all([detalle1, detalle2])
        mock_sistema_session.commit()
        
        # Obtener productos vendidos
        ventas = [nota]
        productos = obtener_productos_vendidos(ventas)
        
        assert len(productos) == 2
        
        # Verificar primer producto
        assert productos[0]['producto'] == "Camisa Azul"
        assert productos[0]['cantidad'] == 2
        assert productos[0]['precio_unitario'] == Decimal("25.00")
        assert productos[0]['subtotal'] == Decimal("50.00")
        assert productos[0]['costo'] == Decimal("10.00")
        
        # Verificar segundo producto
        assert productos[1]['producto'] == "Pantalón Negro"
        assert productos[1]['cantidad'] == 3
        assert productos[1]['precio_unitario'] == Decimal("30.00")
        assert productos[1]['subtotal'] == Decimal("90.00")
        assert productos[1]['costo'] == Decimal("15.00")

    def test_obtener_productos_vendidos_sin_ventas(self, mock_sistema_session):
        """Test para obtener productos vendidos sin ventas"""
        from sistema import obtener_productos_vendidos
        
        productos = obtener_productos_vendidos([])
        assert productos == []

    def test_obtener_notas_filtradas_sin_filtros(self, mock_sistema_session):
        """Test para obtener notas filtradas sin aplicar filtros"""
        from sistema import obtener_notas_filtradas
        
        # Crear clientes y notas canceladas
        cliente1 = Cliente(nombre="Juan Pérez", dni="111", direccion="Dir1", telefono="111")
        cliente2 = Cliente(nombre="María García", dni="222", direccion="Dir2", telefono="222")
        mock_sistema_session.add_all([cliente1, cliente2])
        mock_sistema_session.commit()
        
        nota1 = NotaVenta(id_cliente=cliente1.id_cliente, fecha=date.today(), 
                         total=Decimal("100.00"), estado="Cancelado", fecha_venta=date.today())
        nota2 = NotaVenta(id_cliente=cliente2.id_cliente, fecha=date.today(), 
                         total=Decimal("200.00"), estado="Cancelado", fecha_venta=date.today())
        nota3 = NotaVenta(id_cliente=cliente1.id_cliente, fecha=date.today(), 
                         total=Decimal("150.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add_all([nota1, nota2, nota3])
        mock_sistema_session.commit()
        
        # Obtener notas sin filtros (solo canceladas)
        notas = obtener_notas_filtradas({})
        
        assert len(notas) == 2  # Solo las canceladas
        
    def test_obtener_notas_filtradas_por_id(self, mock_sistema_session):
        """Test para filtrar notas por ID"""
        from sistema import obtener_notas_filtradas
        
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota1 = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                         total=Decimal("100.00"), estado="Cancelado", fecha_venta=date.today())
        nota2 = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                         total=Decimal("200.00"), estado="Cancelado", fecha_venta=date.today())
        mock_sistema_session.add_all([nota1, nota2])
        mock_sistema_session.commit()
        
        # Filtrar por ID
        filtros = {"ID Venta": str(nota1.id_nota)}
        notas = obtener_notas_filtradas(filtros)
        
        assert len(notas) >= 1
        assert any(nota.id_nota == nota1.id_nota for nota in notas)

    def test_obtener_notas_filtradas_por_cliente(self, mock_sistema_session):
        """Test para filtrar notas por nombre de cliente"""
        from sistema import obtener_notas_filtradas
        
        cliente1 = Cliente(nombre="Juan Pérez", dni="111", direccion="Dir1", telefono="111")
        cliente2 = Cliente(nombre="María García", dni="222", direccion="Dir2", telefono="222")
        mock_sistema_session.add_all([cliente1, cliente2])
        mock_sistema_session.commit()
        
        nota1 = NotaVenta(id_cliente=cliente1.id_cliente, fecha=date.today(), 
                         total=Decimal("100.00"), estado="Cancelado", fecha_venta=date.today())
        nota2 = NotaVenta(id_cliente=cliente2.id_cliente, fecha=date.today(), 
                         total=Decimal("200.00"), estado="Cancelado", fecha_venta=date.today())
        mock_sistema_session.add_all([nota1, nota2])
        mock_sistema_session.commit()
        
        # Filtrar por nombre de cliente
        filtros = {"Cliente": "Juan"}
        notas = obtener_notas_filtradas(filtros)
        
        assert len(notas) == 1
        assert notas[0].nombre_cliente == "Juan Pérez"

    def test_obtener_notas_filtradas_por_rango_fechas(self, mock_sistema_session):
        """Test para filtrar notas por rango de fechas"""
        from sistema import obtener_notas_filtradas
        from datetime import timedelta
        
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        fecha_hoy = date.today()
        fecha_ayer = fecha_hoy - timedelta(days=1)
        fecha_hace_5_dias = fecha_hoy - timedelta(days=5)
        
        nota1 = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_ayer, 
                         total=Decimal("100.00"), estado="Cancelado", fecha_venta=fecha_ayer)
        nota2 = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_hace_5_dias, 
                         total=Decimal("200.00"), estado="Cancelado", fecha_venta=fecha_hace_5_dias)
        mock_sistema_session.add_all([nota1, nota2])
        mock_sistema_session.commit()
        
        # Filtrar por rango de fechas (últimos 3 días)
        filtros = {
            "Fecha Inicio": fecha_hoy - timedelta(days=3),
            "Fecha Fin": fecha_hoy
        }
        notas = obtener_notas_filtradas(filtros)
        
        assert len(notas) == 1
        assert notas[0].id_nota == nota1.id_nota

    def test_total_menos_amortizacion(self, mock_sistema_session):
        """Test para calcular total menos amortizaciones"""
        from sistema import total_menos_amortizacion
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Agregar amortizaciones
        amortizacion1 = Amortizacion(id_nota=nota.id_nota, monto=Decimal("30.00"), fecha=date.today())
        amortizacion2 = Amortizacion(id_nota=nota.id_nota, monto=Decimal("20.00"), fecha=date.today())
        mock_sistema_session.add_all([amortizacion1, amortizacion2])
        mock_sistema_session.commit()
        
        # Calcular total menos amortizaciones (100 - 30 - 20 = 50)
        total_restante = total_menos_amortizacion(nota.id_nota)
        
        assert total_restante == Decimal("50.00")

    def test_total_menos_amortizacion_sin_amortizaciones(self, mock_sistema_session):
        """Test para calcular total sin amortizaciones"""
        from sistema import total_menos_amortizacion
        
        # Crear cliente y nota sin amortizaciones
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Total debe ser igual al original
        total_restante = total_menos_amortizacion(nota.id_nota)
        
        assert total_restante == Decimal("100.00")

    def test_actualizar_estado_pedido_exitoso(self, mock_sistema_session):
        """Test para actualizar estado de pedido exitosamente"""
        from sistema import actualizar_estado_pedido
        
        # Crear cliente y nota
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        mock_sistema_session.add(cliente)
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("100.00"), estado="Pendiente", fecha_venta=date.today(),
                        estado_pedido="ABIERTO")
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        # Actualizar estado
        resultado = actualizar_estado_pedido(nota.id_nota, "CERRADO")
        
        assert resultado is True
        nota_actualizada = mock_sistema_session.query(NotaVenta).filter_by(id_nota=nota.id_nota).first()
        assert nota_actualizada.estado_pedido == "CERRADO"

    def test_actualizar_estado_pedido_nota_inexistente(self, mock_sistema_session):
        """Test para actualizar estado de pedido con nota inexistente"""
        from sistema import actualizar_estado_pedido
        
        # Intentar actualizar nota inexistente
        with pytest.raises(ValueError) as exc_info:
            actualizar_estado_pedido(999, "CERRADO")
        
        assert "no existe" in str(exc_info.value) or "Nota" in str(exc_info.value)

    def test_obtener_reporte_por_mes_anio(self, mock_sistema_session):
        """Test para obtener reporte filtrado por mes y año"""
        from sistema import obtener_reporte
        
        # Crear cliente, producto y notas
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        # Crear nota con fecha específica
        fecha_especifica = date(2024, 3, 15)
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_especifica, 
                        total=Decimal("50.00"), estado="Cancelado", fecha_venta=fecha_especifica)
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("25.00"), 
            talla="M", color="Rojo", subtotal=Decimal("50.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Obtener reporte de marzo 2024
        reporte = obtener_reporte(mes=3, anio=2024)
        
        assert len(reporte) >= 1
        # Verificar estructura del reporte
        assert hasattr(reporte[0], 'id_nota_venta')
        assert hasattr(reporte[0], 'producto')
        assert hasattr(reporte[0], 'cliente')
        assert hasattr(reporte[0], 'cantidad')
        assert hasattr(reporte[0], 'precio_unitario')

    def test_obtener_reporte_por_rango_fechas(self, mock_sistema_session):
        """Test para obtener reporte filtrado por rango de fechas"""
        from sistema import obtener_reporte
        from datetime import timedelta
        
        # Crear cliente, producto y notas
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        fecha_hoy = date.today()
        fecha_ayer = fecha_hoy - timedelta(days=1)
        fecha_hace_5_dias = fecha_hoy - timedelta(days=5)
        
        # Nota dentro del rango
        nota1 = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_ayer, 
                         total=Decimal("50.00"), estado="Cancelado", fecha_venta=fecha_ayer)
        # Nota fuera del rango
        nota2 = NotaVenta(id_cliente=cliente.id_cliente, fecha=fecha_hace_5_dias, 
                         total=Decimal("100.00"), estado="Cancelado", fecha_venta=fecha_hace_5_dias)
        mock_sistema_session.add_all([nota1, nota2])
        mock_sistema_session.commit()
        
        detalle1 = DetalleNotaVenta(
            id_nota=nota1.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("25.00"), 
            talla="M", color="Rojo", subtotal=Decimal("50.00")
        )
        detalle2 = DetalleNotaVenta(
            id_nota=nota2.id_nota, id_producto=producto.id_producto,
            cantidad=4, precio_unitario=Decimal("25.00"), 
            talla="L", color="Azul", subtotal=Decimal("100.00")
        )
        mock_sistema_session.add_all([detalle1, detalle2])
        mock_sistema_session.commit()
        
        # Obtener reporte de los últimos 3 días
        fecha_desde = fecha_hoy - timedelta(days=3)
        fecha_hasta = fecha_hoy
        reporte = obtener_reporte(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        
        # Debe retornar solo la nota dentro del rango
        assert len(reporte) == 1
        assert reporte[0].id_nota_venta == nota1.id_nota

    def test_obtener_reporte_sin_filtros(self, mock_sistema_session):
        """Test para obtener reporte sin filtros (todas las ventas)"""
        from sistema import obtener_reporte
        
        # Crear cliente, producto y notas
        cliente = Cliente(nombre="Cliente Test", dni="123", direccion="Test", telefono="123")
        producto = Producto(nombre="Producto Test", stock=100, costo=Decimal("10.00"))
        mock_sistema_session.add_all([cliente, producto])
        mock_sistema_session.commit()
        
        nota = NotaVenta(id_cliente=cliente.id_cliente, fecha=date.today(), 
                        total=Decimal("50.00"), estado="Cancelado", fecha_venta=date.today())
        mock_sistema_session.add(nota)
        mock_sistema_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota, id_producto=producto.id_producto,
            cantidad=2, precio_unitario=Decimal("25.00"), 
            talla="M", color="Rojo", subtotal=Decimal("50.00")
        )
        mock_sistema_session.add(detalle)
        mock_sistema_session.commit()
        
        # Obtener reporte sin filtros
        reporte = obtener_reporte()
        
        assert len(reporte) >= 1