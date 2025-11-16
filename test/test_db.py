import pytest
import os
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys
# Agregar la raíz del proyecto al path si no está
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar las clases de tu db.py
from db import (
    Base, Cliente, Producto, Amortizacion, NotaVenta, 
    DetalleNotaVenta
)

class TestDatabaseModels:
    """Suite de tests para los modelos de la base de datos"""
    
    @pytest.fixture(scope="function")
    def test_session(self):
        """Fixture para crear una sesión de test"""
        # Crear una base de datos en memoria para tests
        test_engine = create_engine("sqlite:///:memory:")
        TestSession = sessionmaker(bind=test_engine)
        Base.metadata.create_all(test_engine)
        
        session = TestSession()
        yield session
        session.close()
    
    @pytest.fixture
    def sample_cliente(self):
        """Fixture para crear un cliente de ejemplo"""
        return Cliente(
            dni="12345678",
            nombre="Juan Pérez",
            direccion="Av. Lima 123",
            telefono="987654321"
        )
    
    @pytest.fixture
    def sample_producto(self):
        """Fixture para crear un producto de ejemplo"""
        return Producto(
            nombre="Producto Test",
            costo=Decimal("10.50"),
            stock=100,
            precio_inicial=Decimal("15.00")
        )

    def test_cliente_creation(self, test_session, sample_cliente):
        """Test para crear un cliente"""
        test_session.add(sample_cliente)
        test_session.commit()
        
        cliente_db = test_session.query(Cliente).filter_by(dni="12345678").first()
        assert cliente_db is not None
        assert cliente_db.nombre == "Juan Pérez"
        assert cliente_db.direccion == "Av. Lima 123"
        assert cliente_db.telefono == "987654321"
    
    def test_cliente_repr(self, sample_cliente):
        """Test para el método __repr__ de Cliente"""
        sample_cliente.id_cliente = 1
        repr_str = repr(sample_cliente)
        expected = "<Cliente(id_cliente=1, nombre=Juan Pérez, dni=12345678, direccion=Av. Lima 123, telefono=987654321)>"
        assert repr_str == expected
    
    def test_cliente_dni_unique_constraint(self, test_session, sample_cliente):
        """Test para verificar que el DNI es único"""
        # Crear primer cliente
        test_session.add(sample_cliente)
        test_session.commit()
        
        # Intentar crear otro cliente con el mismo DNI
        cliente_duplicado = Cliente(
            dni="12345678",
            nombre="Otro Cliente",
            direccion="Otra dirección",
            telefono="123456789"
        )
        test_session.add(cliente_duplicado)
        
        with pytest.raises(IntegrityError):
            test_session.commit()
    
    def test_producto_creation(self, test_session, sample_producto):
        """Test para crear un producto"""
        test_session.add(sample_producto)
        test_session.commit()
        
        producto_db = test_session.query(Producto).filter_by(nombre="Producto Test").first()
        assert producto_db is not None
        assert producto_db.costo == Decimal("10.50")
        assert producto_db.stock == 100
        assert producto_db.precio_inicial == Decimal("15.00")
    
    def test_producto_nombre_unique_constraint(self, test_session, sample_producto):
        """Test para verificar que el nombre del producto es único"""
        # Crear primer producto
        test_session.add(sample_producto)
        test_session.commit()
        
        # Intentar crear otro producto con el mismo nombre
        producto_duplicado = Producto(
            nombre="Producto Test",
            costo=Decimal("20.00"),
            stock=50,
            precio_inicial=Decimal("25.00")
        )
        test_session.add(producto_duplicado)
        
        with pytest.raises(IntegrityError):
            test_session.commit()
    
    def test_nota_venta_creation(self, test_session, sample_cliente):
        """Test para crear una nota de venta"""
        test_session.add(sample_cliente)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today(),
            observaciones="Test observaciones",
            estado_pedido="En proceso"
        )
        test_session.add(nota)
        test_session.commit()
        
        nota_db = test_session.query(NotaVenta).first()
        assert nota_db is not None
        assert nota_db.total == Decimal("100.00")
        assert nota_db.estado == "Pendiente"
        assert nota_db.observaciones == "Test observaciones"
        assert nota_db.estado_pedido == "En proceso"
    
    def test_amortizacion_creation(self, test_session, sample_cliente):
        #Test para crear una amortización
        # Crear cliente y nota de venta
        test_session.add(sample_cliente)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        test_session.add(nota)
        test_session.commit()
        
        # Crear amortización
        amortizacion = Amortizacion(
            id_nota=nota.id_nota,
            monto=Decimal("50.00"),
            fecha=date.today()
        )
        test_session.add(amortizacion)
        test_session.commit()
        
        amortizacion_db = test_session.query(Amortizacion).first()
        assert amortizacion_db is not None
        assert amortizacion_db.monto == Decimal("50.00")
        assert amortizacion_db.fecha == date.today()
    
    def test_detalle_nota_venta_creation(self, test_session, sample_cliente, sample_producto):
        #Test para crear un detalle de nota de venta
        # Crear cliente, producto y nota de venta
        test_session.add(sample_cliente)
        test_session.add(sample_producto)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        test_session.add(nota)
        test_session.commit()
        
        # Crear detalle
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota,
            id_producto=sample_producto.id_producto,
            cantidad=2,
            precio_unitario=Decimal("15.00"),
            color="Rojo",
            talla="M",
            subtotal=Decimal("30.00")
        )
        test_session.add(detalle)
        test_session.commit()
        
        detalle_db = test_session.query(DetalleNotaVenta).first()
        assert detalle_db is not None
        assert detalle_db.cantidad == 2
        assert detalle_db.precio_unitario == Decimal("15.00")
        assert detalle_db.color == "Rojo"
        assert detalle_db.talla == "M"
        assert detalle_db.subtotal == Decimal("30.00")
    
    def test_relationships_cliente_notas(self, test_session, sample_cliente):
        #Test para verificar la relación Cliente -> NotaVenta
        test_session.add(sample_cliente)
        test_session.commit()
        
        # Crear dos notas para el mismo cliente
        nota1 = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        nota2 = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("200.00"),
            estado="Pagado",
            fecha_venta=date.today()
        )
        test_session.add_all([nota1, nota2])
        test_session.commit()
        
        # Verificar la relación
        cliente_db = test_session.query(Cliente).filter_by(dni="12345678").first()
        assert len(cliente_db.notas) == 2
        assert cliente_db.notas[0].total in [Decimal("100.00"), Decimal("200.00")]
    
    def test_relationships_nota_amortizaciones(self, test_session, sample_cliente):
        #Test para verificar la relación NotaVenta -> Amortizacion
        test_session.add(sample_cliente)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        test_session.add(nota)
        test_session.commit()
        
        # Crear dos amortizaciones
        amortizacion1 = Amortizacion(
            id_nota=nota.id_nota,
            monto=Decimal("30.00"),
            fecha=date.today()
        )
        amortizacion2 = Amortizacion(
            id_nota=nota.id_nota,
            monto=Decimal("20.00"),
            fecha=date.today()
        )
        test_session.add_all([amortizacion1, amortizacion2])
        test_session.commit()
        
        # Verificar la relación
        nota_db = test_session.query(NotaVenta).first()
        assert len(nota_db.amortizaciones) == 2
        montos = [amor.monto for amor in nota_db.amortizaciones]
        assert Decimal("30.00") in montos
        assert Decimal("20.00") in montos
    
    def test_relationships_nota_detalles(self, test_session, sample_cliente, sample_producto):
        #Test para verificar la relación NotaVenta -> DetalleNotaVenta
        test_session.add(sample_cliente)
        test_session.add(sample_producto)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        test_session.add(nota)
        test_session.commit()
        
        # Crear dos detalles
        detalle1 = DetalleNotaVenta(
            id_nota=nota.id_nota,
            id_producto=sample_producto.id_producto,
            cantidad=2,
            precio_unitario=Decimal("15.00"),
            color="Rojo",
            talla="M",
            subtotal=Decimal("30.00")
        )
        detalle2 = DetalleNotaVenta(
            id_nota=nota.id_nota,
            id_producto=sample_producto.id_producto,
            cantidad=1,
            precio_unitario=Decimal("15.00"),
            color="Azul",
            talla="L",
            subtotal=Decimal("15.00")
        )
        test_session.add_all([detalle1, detalle2])
        test_session.commit()
        
        # Verificar la relación
        nota_db = test_session.query(NotaVenta).first()
        assert len(nota_db.detalles) == 2
        colores = [detalle.color for detalle in nota_db.detalles]
        assert "Rojo" in colores
        assert "Azul" in colores
    
"""    def test_cascade_delete_amortizaciones(self, test_session, sample_cliente):
        #Test para verificar la eliminación en cascada de amortizaciones
        test_session.add(sample_cliente)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        test_session.add(nota)
        test_session.commit()
        
        amortizacion = Amortizacion(
            id_nota=nota.id_nota,
            monto=Decimal("50.00"),
            fecha=date.today()
        )
        test_session.add(amortizacion)
        test_session.commit()
        
        # Verificar que existen
        assert test_session.query(NotaVenta).count() == 1
        assert test_session.query(Amortizacion).count() == 1
        
        # Eliminar la nota
        test_session.delete(nota)
        test_session.commit()
        
        # Verificar que la amortización también se eliminó
        assert test_session.query(NotaVenta).count() == 0
        assert test_session.query(Amortizacion).count() == 0
    
    def test_cascade_delete_detalles(self, test_session, sample_cliente, sample_producto):
        #Test para verificar la eliminación en cascada de detalles
        test_session.add(sample_cliente)
        test_session.add(sample_producto)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        test_session.add(nota)
        test_session.commit()
        
        detalle = DetalleNotaVenta(
            id_nota=nota.id_nota,
            id_producto=sample_producto.id_producto,
            cantidad=2,
            precio_unitario=Decimal("15.00"),
            color="Rojo",
            talla="M",
            subtotal=Decimal("30.00")
        )
        test_session.add(detalle)
        test_session.commit()
        
        # Verificar que existen
        assert test_session.query(NotaVenta).count() == 1
        assert test_session.query(DetalleNotaVenta).count() == 1
        
        # Eliminar la nota
        test_session.delete(nota)
        test_session.commit()
        
        # Verificar que el detalle también se eliminó
        assert test_session.query(NotaVenta).count() == 0
        assert test_session.query(DetalleNotaVenta).count() == 0
    
    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"})
    def test_database_url_environment(self):
        #Test para verificar que se usa la variable de entorno DATABASE_URL
        with patch('db.create_engine') as mock_create_engine:
            # Re-importar para que tome la nueva variable de entorno
            import importlib
            import db
            importlib.reload(db)
            
            mock_create_engine.assert_called_with("sqlite:///:memory:")
    
    def test_amortizacion_default_date(self, test_session, sample_cliente):
        #Test para verificar que la fecha por defecto se asigna correctamente
        test_session.add(sample_cliente)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=sample_cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today()
        )
        test_session.add(nota)
        test_session.commit()
        
        # Crear amortización sin especificar fecha
        amortizacion = Amortizacion(
            id_nota=nota.id_nota,
            monto=Decimal("50.00")
        )
        test_session.add(amortizacion)
        test_session.commit()
        
        amortizacion_db = test_session.query(Amortizacion).first()
        assert amortizacion_db.fecha == date.today()"""




"""class TestNullableFields:
    
    def test_producto_precio_inicial_nullable(self, test_session):
        producto = Producto(
            nombre="Producto Sin Precio",
            costo=Decimal("10.00"),
            stock=50,
            precio_inicial=None
        )
        test_session.add(producto)
        test_session.commit()
        
        producto_db = test_session.query(Producto).filter_by(nombre="Producto Sin Precio").first()
        assert producto_db.precio_inicial is None
    
    def test_nota_venta_observaciones_nullable(self, test_session):
        # Necesitamos un cliente primero
        cliente = Cliente(dni="87654321", nombre="Test Cliente")
        test_session.add(cliente)
        test_session.commit()
        
        nota = NotaVenta(
            id_cliente=cliente.id_cliente,
            fecha=date.today(),
            total=Decimal("100.00"),
            estado="Pendiente",
            fecha_venta=date.today(),
            observaciones=None,
            estado_pedido=None
        )
        test_session.add(nota)
        test_session.commit()
        
        nota_db = test_session.query(NotaVenta).first()
        assert nota_db.observaciones is None
        assert nota_db.estado_pedido is None"""