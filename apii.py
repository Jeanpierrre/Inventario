from flask import Flask, request, jsonify, g, send_from_directory
from db import Cliente, Producto, NotaVenta, DetalleNotaVenta, Session
from datetime import date, datetime
from sqlalchemy import cast, String
from sqlalchemy.orm import joinedload
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Función para obtener la sesión del contexto de la petición
def get_db():
    if 'db' not in g:
        g.db = Session()
    return g.db

# Cerrar la sesión al final de cada petición
@app.teardown_appcontext
def teardown_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Función auxiliar para serializar fechas
def serialize_date(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    return obj

# Función auxiliar para convertir objetos SQLAlchemy a diccionario
def to_dict(obj):
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, date):
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value
    return result

@app.route('/api/productos', methods=['GET'])
def obtener_todos_los_productos():
    """
    GET /api/productos
    Retorna todos los productos ordenados por id_producto
    """
    try:
        session = get_db()
        productos = session.query(Producto).order_by(Producto.id_producto).all()
        productos_dict = [to_dict(producto) for producto in productos]
        
        return jsonify({
            'success': True,
            'data': productos_dict,
            'count': len(productos_dict)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/productos/<int:id_producto>', methods=['GET'])
def obtener_producto_por_id(id_producto):
    """
    GET /api/productos/{id}
    Retorna un producto específico por su ID
    """
    try:
        session = get_db()
        producto = session.query(Producto).filter_by(id_producto=id_producto).first()
        
        if not producto:
            return jsonify({
                'success': False,
                'error': 'Producto no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': to_dict(producto)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notas/filtradas', methods=['POST'])
def obtener_notas_filtradas():
    """
    POST /api/notas/filtradas
    Retorna notas filtradas según criterios específicos
    
    Body ejemplo:
    {
        "ID Venta": "123",
        "Cliente": "Juan",
        "Fecha Inicio": "2024-01-01",
        "Fecha Fin": "2024-12-31"
    }
    """
    try:
        session = get_db()
        filtros_activos = request.json or {}
        
        # Consulta base con join a Cliente
        query = session.query(
            NotaVenta.id_nota,
            NotaVenta.fecha_venta,
            NotaVenta.total,
            Cliente.nombre.label("nombre_cliente")
        ).join(Cliente, NotaVenta.id_cliente == Cliente.id_cliente, isouter=True)\
         .filter(NotaVenta.estado.ilike('%cancelado%'))

        # Aplicar filtros
        if filtros_activos.get("ID Venta"):
            query = query.filter(cast(NotaVenta.id_nota, String).ilike(f"%{filtros_activos['ID Venta']}%"))
        
        if filtros_activos.get("Cliente"):
            query = query.filter(Cliente.nombre.ilike(f"%{filtros_activos['Cliente']}%"))
        
        if filtros_activos.get("Fecha Inicio"):
            fecha_inicio = datetime.strptime(filtros_activos["Fecha Inicio"], "%Y-%m-%d").date()
            query = query.filter(NotaVenta.fecha_venta >= fecha_inicio)
        
        if filtros_activos.get("Fecha Fin"):
            fecha_fin = datetime.strptime(filtros_activos["Fecha Fin"], "%Y-%m-%d").date()
            query = query.filter(NotaVenta.fecha_venta <= fecha_fin)

        # Ejecutar consulta
        notas = query.order_by(NotaVenta.fecha_venta.asc(), NotaVenta.id_nota.asc()).all()
        
        # Convertir resultados a diccionario
        notas_dict = []
        for nota in notas:
            notas_dict.append({
                'id_nota': nota.id_nota,
                'fecha_venta': serialize_date(nota.fecha_venta),
                'total': float(nota.total) if nota.total else 0,
                'nombre_cliente': nota.nombre_cliente
            })
        
        return jsonify({
            'success': True,
            'data': notas_dict,
            'count': len(notas_dict)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notas', methods=['POST'])
def crear_nota_venta():
    """
    POST /api/notas
    Crea una nueva nota de venta
    
    Body ejemplo:
    {
        "id_cliente": 1,
        "productos_cantidades": [
            [1, 2, 50.0, "M", "Rojo"],
            [2, 1, 25.0, "L", "Azul"]
        ],
        "observaciones": "Nota de prueba"
    }
    """
    session = get_db()
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        id_cliente = data.get('id_cliente')
        productos_cantidades = data.get('productos_cantidades', [])
        observaciones = data.get('observaciones')
        
        if not id_cliente:
            return jsonify({
                'success': False,
                'error': 'id_cliente es requerido'
            }), 400
        
        if not productos_cantidades:
            return jsonify({
                'success': False,
                'error': 'productos_cantidades es requerido'
            }), 400
        
        # Verificar que el cliente existe
        cliente = session.query(Cliente).filter_by(id_cliente=id_cliente).first()
        if not cliente:
            return jsonify({
                'success': False,
                'error': 'El cliente no existe'
            }), 404
        
        # Crear nueva nota de venta
        nueva_nota = NotaVenta(
            id_cliente=id_cliente,
            fecha=date.today(),
            total=0,
            estado="Pendiente",
            observaciones=observaciones,
            estado_pedido="ABIERTO"
        )
        
        session.add(nueva_nota)
        session.flush()  # Para obtener el id_nota
        
        total_venta = 0
        
        # Procesar productos
        for producto_data in productos_cantidades:
            if len(producto_data) != 5:
                session.rollback()
                return jsonify({
                    'success': False,
                    'error': 'Cada producto debe tener: [id_producto, cantidad, precio_unitario, talla, color]'
                }), 400
            
            id_producto, cantidad, precio_unitario, talla, color = producto_data
            
            # Verificar que el producto existe
            producto = session.query(Producto).filter_by(id_producto=id_producto).first()
            if not producto:
                session.rollback()
                return jsonify({
                    'success': False,
                    'error': f'El producto con ID {id_producto} no existe'
                }), 404
            
            # Verificar stock
            if producto.stock < cantidad:
                session.rollback()
                return jsonify({
                    'success': False,
                    'error': f'No hay suficiente stock para el producto {producto.nombre}. Stock disponible: {producto.stock}'
                }), 400
            
            subtotal = round(precio_unitario * cantidad, 2)
            
            # Crear detalle de nota
            detalle_nota = DetalleNotaVenta(
                id_nota=nueva_nota.id_nota,
                id_producto=id_producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                talla=talla,
                color=color,
                subtotal=subtotal
            )
            session.add(detalle_nota)
            total_venta += subtotal
        
        # Actualizar total de la nota
        nueva_nota.total = round(total_venta, 2)
        session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id_nota': nueva_nota.id_nota,
                'total': total_venta
            },
            'message': f'Nota de venta creada exitosamente con ID: {nueva_nota.id_nota}'
        }), 201
        
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notas/<int:id_nota>/confirmar-venta', methods=['POST'])
def agregar_venta(id_nota):
    """
    POST /api/notas/{id}/confirmar-venta
    Confirma una venta (reduce stock y cambia estado a "Cancelado")
    """
    session = get_db()
    try:
        # Verificar que la nota existe
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if not nota:
            return jsonify({
                'success': False,
                'error': 'La nota de venta no existe'
            }), 404
        
        # Verificar stock antes de proceder
        detalles = session.query(DetalleNotaVenta).filter_by(id_nota=id_nota).all()
        
        for detalle in detalles:
            producto = session.query(Producto).filter_by(id_producto=detalle.id_producto).first()
            if not producto:
                return jsonify({
                    'success': False,
                    'error': f'El producto con ID {detalle.id_producto} no existe'
                }), 404
            
            if producto.stock < detalle.cantidad:
                return jsonify({
                    'success': False,
                    'error': f'El producto "{producto.nombre}" no tiene suficiente stock. Disponible: {producto.stock}, Requerido: {detalle.cantidad}'
                }), 400
        
        # Reducir stock de los productos
        for detalle in detalles:
            producto = session.query(Producto).filter_by(id_producto=detalle.id_producto).first()
            producto.stock -= detalle.cantidad
        
        # Cambiar estado de la nota
        nota.estado = "Cancelado"
        nota.fecha_venta = date.today()
        
        session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Venta confirmada exitosamente para la Nota de Venta ID: {id_nota}',
            'data': {
                'id_nota': id_nota,
                'estado': nota.estado,
                'fecha_venta': serialize_date(nota.fecha_venta)
            }
        }), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Ruta de prueba para verificar que la API funciona
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    GET /api/health
    Verificación de estado de la API
    """
    return jsonify({
        'success': True,
        'message': 'API funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    }), 200

# Manejo de errores globales
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500

@app.route('/')
def index():
    return send_from_directory('.', 'frontend.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)