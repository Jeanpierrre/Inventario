from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, DECIMAL, Text, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
from dotenv import load_dotenv
import os
load_dotenv()


Base = declarative_base()

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
class Cliente(Base):
    __tablename__ = 'clientes'
    id_cliente = Column(Integer, primary_key=True)
    dni = Column(String, unique=True, nullable=False)
    nombre = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    notas = relationship("NotaVenta", back_populates="cliente")


    def __repr__(self):
        return (f"<Cliente(id_cliente={self.id_cliente}, nombre={self.nombre}, dni={self.dni}, "
                f"direccion={self.direccion}, telefono={self.telefono})>")
class Producto(Base):
    __tablename__ = 'productos'
    id_producto = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False) 
    costo = Column(DECIMAL)
    stock = Column(Integer)
    precio_inicial = Column(DECIMAL, nullable=True)
class Amortizacion(Base):
    __tablename__ = 'amortizaciones'
    id_amortizacion = Column(Integer, primary_key=True)
    id_nota = Column(Integer, ForeignKey('notas_venta.id_nota'))
    monto = Column(DECIMAL)
    fecha = Column(Date, default=date.today)
    # Relación con la nota de venta
    nota = relationship("NotaVenta", back_populates="amortizaciones")
class NotaVenta(Base):
    __tablename__ = 'notas_venta'
    id_nota = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, ForeignKey('clientes.id_cliente'))
    fecha = Column(Date)
    total = Column(DECIMAL)
    estado = Column(String)
    fecha_venta = Column(Date)
    observaciones = Column(Text, nullable=True) #agregado
    estado_pedido = Column(String, nullable=True) #agregado
    # Relaciones
    cliente = relationship("Cliente", back_populates="notas")
    amortizaciones = relationship("Amortizacion", back_populates="nota", cascade="all, delete")  # Eliminación en cascada
    detalles = relationship("DetalleNotaVenta", back_populates="nota", cascade="all, delete")    # Eliminación en cascada
class DetalleNotaVenta(Base):
    __tablename__ = 'detalle_nota_venta'
    id_detalle = Column(Integer, primary_key=True)
    id_nota = Column(Integer, ForeignKey('notas_venta.id_nota'))
    id_producto = Column(Integer, ForeignKey('productos.id_producto'))
    cantidad = Column(Integer)
    precio_unitario = Column(DECIMAL)  # Precio real del producto en esta venta
    color = Column(String)
    talla = Column(String)
    subtotal = Column(DECIMAL)
    # Relaciones
    nota = relationship("NotaVenta", back_populates="detalles")
    producto = relationship("Producto")

#reiniciar_db()
Base.metadata.create_all(engine)