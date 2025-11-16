from db import Cliente, Producto, NotaVenta, DetalleNotaVenta, Session, Amortizacion
from datetime import date
from sqlalchemy import cast, String, func, or_, and_
import time
from sqlalchemy.orm import joinedload
from calendar import monthrange
session = Session()
from tkinter import messagebox
# Crear la sesión con la base de datos

Text_exito = "Éxito"
Text_Nota_Venta="La nota de venta no existe."

def agregar_cliente(nombre, direccion, telefono, dni):
    """
    Función que agrega un cliente a la base de datos
    desde la interfaz gráfica, validando por DNI y nombre.
    """
    try:
        if not nombre or not dni:
            raise ValueError("El nombre y el DNI son campos obligatorios")
        
        # Verificar si el cliente ya existe por nombre y DNI
        cliente_existente = session.query(Cliente).filter_by(dni=dni, nombre=nombre).first()
        if cliente_existente:
            raise ValueError("El cliente ya existe con este DNI y nombre")
        # Crear el nuevo cliente
        nuevo_cliente = Cliente(
            nombre=nombre,
            direccion=direccion,
            telefono=telefono,
            dni=dni
        )
        session.add(nuevo_cliente)
        session.commit()
        messagebox.showinfo(Text_exito, f"Cliente '{nombre}' creado exitosamente")
    
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", str(e))
    
    finally:
        session.close()
def agregar_producto(nombre, stock, costo, precio_inicial=None):
    """
    Función que agrega un producto a la base de datos
    desde la interfaz gráfica.
    """
    try:
        if not nombre or not stock or not costo:
            raise ValueError("Todos los campos son obligatorios")
        
        # Verificar si el producto ya existe
        producto_existente = session.query(Producto).filter_by(nombre=nombre).first()
        if producto_existente:
            raise ValueError("El producto ya existe con este nombre")
        # Crear el nuevo producto
        nuevo_producto = Producto(
            nombre=nombre,
            stock=stock,
            costo=costo,
            precio_inicial=precio_inicial
        )
        session.add(nuevo_producto)
        session.commit()
        messagebox.showinfo(Text_exito, f"Producto '{nombre}' creado exitosamente")
    
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", str(e))
    
    finally:
        session.close()
def obtener_todos_los_clientes():
    """
    Función que obtiene todos los clientes de la base de datos.
    """
    try:
        clientes = session.query(Cliente).all()
        return clientes
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener los clientes: {e}")
        return []
def obtener_todos_los_productos():
    # Devuelve los productos ordenados por id_producto
    return session.query(Producto).order_by(Producto.id_producto).all()
def obtener_todos_los_productos_1():
    # Devuelve los productos ordenados por id_producto
    try:
        productos = session.query(Producto).all()
        return productos
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener los productos: {e}")
        return []
def obtener_todas_las_notas():
    """
    Función que obtiene todas las notas de venta de la base de datos.
    """
    try:
        notas = session.query(NotaVenta).order_by(NotaVenta.id_nota.asc()).all()
        return notas
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener las notas de venta: {e}")
        return []
def obtener_notas_paginadas(filtro_texto="", page=1, per_page=50, filtro_estado_pedido=None):
    try:
        # Consulta base
        query_base = session.query(NotaVenta).join(Cliente).options(joinedload(NotaVenta.cliente))
        # Filtro por texto (nombre cliente, estado o id)
        if filtro_texto:
            filtro_texto = f"%{filtro_texto.lower()}%"
            query_base = query_base.filter(
                or_(
                    func.lower(Cliente.nombre).like(filtro_texto),
                    func.lower(NotaVenta.estado).like(filtro_texto),
                    func.cast(NotaVenta.id_nota, String).like(filtro_texto)
                )
            )
        # Filtro por estado_pedido (columna NotaVenta.estado_pedido)
        if filtro_estado_pedido:
            query_base = query_base.filter(NotaVenta.estado_pedido == filtro_estado_pedido)
        # Contar total de registros antes de paginar
        total_registros = query_base.count()
        # Obtener datos paginados
        query_paginada = query_base.order_by(NotaVenta.id_nota.desc()) \
                                   .limit(per_page) \
                                   .offset((page - 1) * per_page)
        return query_paginada.all(), total_registros
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener las notas de venta: {e}")
        return [], 0
def eliminar_cliente(id_cliente, tabla_clientes, selected_item):
    """
    Función para eliminar un cliente de la base de datos y de la tabla gráfica.
    
    :param id_cliente: ID del cliente a eliminar.
    :param tabla_clientes: Referencia al widget Treeview que contiene la tabla de clientes.
    :param selected_item: Referencia al item seleccionado en el Treeview.
    """
    try:
        # Buscar al cliente en la base de datos
        cliente = session.query(Cliente).filter_by(id_cliente=id_cliente).first()
        if cliente:
            # Eliminar el cliente de la base de datos
            session.delete(cliente)
            session.commit()
            # Eliminar la fila de la tabla gráfica
            tabla_clientes.delete(selected_item)
            messagebox.showinfo(Text_exito, f"Cliente {cliente.nombre} eliminado correctamente")
        else:
            messagebox.showerror("Error", "Cliente no encontrado en la base de datos")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar el cliente: {e}")
def crear_nota_venta(id_cliente, productos_cantidades, observaciones=None):
    """
    Función para crear una nueva nota de venta.
    
    :param id_cliente: ID del cliente que realiza la compra.
    :param productos_cantidades: Lista de tuplas (id_producto, cantidad).
    :param observaciones: Observaciones adicionales de la nota de venta.
    """
    try:
        # Obtener el cliente
        cliente = session.query(Cliente).filter_by(id_cliente=id_cliente).first()
        if not cliente:
            raise ValueError("El cliente no existe")
        # Crear una nueva instancia de NotaVenta
        nueva_nota = NotaVenta(
            id_cliente=id_cliente,
            fecha=date.today(),
            total=0,  # Se calculará después
            estado="Pendiente",  # Estado inicial de la venta
            observaciones=observaciones,
            estado_pedido="ABIERTO"  # Estado inicial del pedido
        )
        session.add(nueva_nota)
        session.flush()  # Para obtener el id_nota generado automáticamente
        # Total acumulado de la venta
        total_venta = 0
        # Procesar los productos
        for id_producto, cantidad, precio_unitario, talla, color in productos_cantidades:
            producto = session.query(Producto).filter_by(id_producto=id_producto).first()
            if not producto:
                raise ValueError(f"El producto con ID {id_producto} no existe")
            if producto.stock < cantidad:
                raise ValueError(f"No hay suficiente stock para el producto {producto.nombre}")
            subtotal = precio_unitario * cantidad
            subtotal = round(subtotal, 2)  # Redondear a 2 decimales
            # Crear el detalle de la nota de venta
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
            # Descontar el stock del producto
            #producto.stock -= cantidad
            # Sumar al total de la venta
            total_venta += subtotal
        # Actualizar el total de la nota de venta
        nueva_nota.total = round(total_venta,2)
        session.commit()
        return nueva_nota.id_nota, total_venta
    except Exception as e:
        session.rollback()
        raise e
def obtener_producto_por_id(id_producto):
    """
    Función para obtener un producto por su ID.
    
    :param id_producto: ID del producto a buscar.
    :return: Producto si existe, None si no existe.
    """
    return session.query(Producto).filter_by(id_producto=id_producto).first()
def obtener_cliente_por_id(id_cliente):
    """
    Función para obtener un cliente por su ID.
    
    :param id_cliente: ID del cliente a buscar.
    :return: Cliente si existe, None si no existe.
    """
    return session.query(Cliente).filter_by(id_cliente=id_cliente).first()
def obtener_productos_paginados(filtro_texto=None, solo_stock=False, pagina=1, tamanio_pagina=50):
    query = session.query(Producto)
    if filtro_texto:
        texto = f"%{filtro_texto.lower()}%"
        query = query.filter(func.lower(Producto.nombre).like(texto) | 
                             func.cast(Producto.id_producto, String).like(texto))
    if solo_stock:
        query = query.filter(Producto.stock > 0)
    total = query.count()  # Cantidad total de registros que cumplen el filtro
    productos = (query
                .order_by(Producto.id_producto.desc())
                .offset((pagina - 1) * tamanio_pagina)
                .limit(tamanio_pagina)
                .all())
    return productos, total
def obtener_detalles_nota_por_id_nota(id_nota):
    """
    Función para obtener los detalles de una nota de venta por su ID.
    
    :param id_nota: ID de la nota de venta.
    :return: Lista de detalles de la nota de venta.
    """
    return session.query(DetalleNotaVenta).filter_by(id_nota=id_nota).all()
def obtener_nota_venta_por_id(id_nota):
    return session.query(NotaVenta).filter_by(id_nota=id_nota).first()
def agregar_amortizacion(id_nota, monto):
    try:
        nueva_amortizacion = Amortizacion(
            id_nota=id_nota,
            monto=monto
        )
        session.add(nueva_amortizacion)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e 
def eliminar_amortizacion(id_amortizacion):
    try:
        amortizacion = session.query(Amortizacion).filter_by(id_amortizacion=id_amortizacion).first()
        if not amortizacion:
            raise ValueError("La amortización no existe.")
        session.delete(amortizacion)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
def obtener_amortizaciones_por_id_nota(id_nota):
    """
    Función para obtener todas las amortizaciones asociadas a una nota de venta por su ID.
    
    :param id_nota: ID de la nota de venta.
    :return: Lista de amortizaciones asociadas a la nota de venta.
    """
    return session.query(Amortizacion).filter_by(id_nota=id_nota).all()
def agregar_venta(id_nota):
    try:
        # Obtener la nota de venta
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if not nota:
            raise ValueError(Text_Nota_Venta)
        # Verificar que haya suficientes productos en stock antes de proceder
        detalles = session.query(DetalleNotaVenta).filter_by(id_nota=id_nota).all()
        for detalle in detalles:
            producto = session.query(Producto).filter_by(id_producto=detalle.id_producto).first()
            if not producto:
                raise ValueError(f"El producto con ID {detalle.id_producto} no existe.")
            if producto.stock < detalle.cantidad:
                raise ValueError(f"El producto '{producto.nombre}' no tiene suficiente stock. Disponible: {producto.stock}, Requerido: {detalle.cantidad}.")
        # Reducir el stock de los productos asociados a la nota de venta
        for detalle in detalles:
            producto = session.query(Producto).filter_by(id_producto=detalle.id_producto).first()
            producto.stock -= detalle.cantidad
        # Cambiar el estado de la nota de venta a "Cancelado"
        nota.estado = "Cancelado"
        nota.fecha_venta = date.today()
        
        session.commit()
        messagebox.showinfo(Text_exito, f"Venta confirmada exitosamente para la Nota de Venta ID: {id_nota}")
    
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo confirmar la venta: {e}")
    
    finally:
        session.close()
def modificar_producto(id_producto, nombre, stock, costo, precio_inicial=None):
    """
    Modificando función para incluir precio_inicial
    """
    try:
        # Obtener el producto existente
        producto = session.query(Producto).filter_by(id_producto=id_producto).first()
        if not producto:
            raise ValueError("El producto no existe.")
        # Actualizar los campos del producto
        producto.nombre = nombre
        producto.stock = stock
        producto.costo = costo
        producto.precio_inicial = precio_inicial
        session.commit()
        messagebox.showinfo(Text_exito, f"Producto '{producto.nombre}' modificado exitosamente.")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo modificar el producto: {e}")
    finally:
        session.close()
def eliminar_producto(id_producto):
    try:
        # Obtener el producto existente
        producto = session.query(Producto).filter_by(id_producto=id_producto).first()
        if not producto:
            raise ValueError("El producto no existe.")
        # Confirmar la eliminación
        session.delete(producto)
        session.commit()
        messagebox.showinfo(Text_exito, f"Producto con ID {id_producto} eliminado exitosamente.")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")
    finally:
        session.close()
def obtener_costo_total_inventario():
    """
    Calcula la sumatoria del costo total del inventario.
    (Costo unitario * Stock) para cada producto y luego suma todos los valores.
    """
    try:
        costo_total = session.query(func.sum(Producto.costo * Producto.stock)).scalar()
        return costo_total if costo_total else 0  # Retorna 0 si no hay productos
    except Exception as e:
        messagebox.showerror("Error", f"Error al calcular el costo total del inventario: {e}")
        return 0
def modificar_cliente(id_cliente, nombre, direccion, telefono, dni):
    try:
        # Obtener el cliente existente
        cliente = session.query(Cliente).filter_by(id_cliente=id_cliente).first()
        if not cliente:
            raise ValueError("El cliente no existe.")
        # Actualizar los datos del cliente
        cliente.nombre = nombre
        cliente.direccion = direccion
        cliente.telefono = telefono
        cliente.dni = dni
        session.commit()
        messagebox.showinfo(Text_exito, f"Cliente '{nombre}' modificado exitosamente.")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo modificar el cliente: {e}")
    finally:
        session.close()
def eliminar_nota_venta(id_nota):
    try:
        # Obtener la nota de venta existente
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if not nota:
            raise ValueError(Text_Nota_Venta)
        # Confirmar la eliminación
        session.delete(nota)
        session.commit()
        messagebox.showinfo(Text_exito, f"Nota de Venta con ID {id_nota} eliminada exitosamente.")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar la nota de venta: {e}")
    finally:
        session.close()
def actualizar_observaciones_nota(id_nota, observaciones):
    """
    Nueva función para actualizar observaciones de una nota de venta
    """
    try:
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if not nota:
            raise ValueError(Text_Nota_Venta)
        
        nota.observaciones = observaciones
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
def obtener_observaciones_nota(id_nota):
    try:
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if not nota:
            raise ValueError(Text_Nota_Venta)
        
        return nota.observaciones
    except Exception as e:
        session.rollback()
        raise e
def actualizar_nota_venta_mejorada(id_nota, nuevos_detalles, productos_a_eliminar):
    """
    Versión mejorada que permite actualizar productos existentes sin eliminar todo
    """
    try:
        # Primero eliminar solo los productos marcados para eliminar
        for id_producto in productos_a_eliminar:
            session.query(DetalleNotaVenta).filter_by(id_nota=id_nota, id_producto=id_producto).delete()
        detalles_existentes = session.query(DetalleNotaVenta).filter_by(id_nota=id_nota).all()
        
        # Crear diccionario de detalles existentes por id_producto
        detalles_dict = {detalle.id_producto: detalle for detalle in detalles_existentes}
        
        total = 0
        productos_procesados = set()
        
        for detalle_data in nuevos_detalles:
            id_producto, cantidad, precio_unitario, color, talla, subtotal = detalle_data
            productos_procesados.add(id_producto)
            
            if id_producto in detalles_dict:
                detalle_existente = detalles_dict[id_producto]
                detalle_existente.cantidad = cantidad
                detalle_existente.precio_unitario = precio_unitario
                detalle_existente.color = color
                detalle_existente.talla = talla
                detalle_existente.subtotal = round(subtotal, 2)
            else:
                nuevo_detalle = DetalleNotaVenta(
                    id_nota=id_nota,
                    id_producto=id_producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    color=color,
                    talla=talla,
                    subtotal=round(subtotal, 2)
                )
                session.add(nuevo_detalle)
            
            total += subtotal
        
        for id_producto, detalle in detalles_dict.items():
            if id_producto not in productos_procesados:
                session.delete(detalle)
        
        # Actualizar el total de la nota de venta
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if nota:
            nota.total = round(total, 2)
        session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar la nota de venta: {e}")
        raise e
def actualizar_detalle_producto(id_nota, id_producto, cantidad=None, precio_unitario=None, color=None, talla=None):
    """
    Actualiza campos específicos de un detalle de producto sin afectar otros
    """
    try:
        detalle = session.query(DetalleNotaVenta).filter_by(
            id_nota=id_nota, 
            id_producto=id_producto
        ).first()
        
        if not detalle:
            raise ValueError(f"No se encontró el detalle para el producto {id_producto} en la nota {id_nota}")
        
        # Actualizar solo los campos proporcionados
        if cantidad is not None:
            detalle.cantidad = cantidad
        if precio_unitario is not None:
            detalle.precio_unitario = precio_unitario
        if color is not None:
            detalle.color = color
        if talla is not None:
            detalle.talla = talla
            
        # Recalcular subtotal
        detalle.subtotal = round(detalle.cantidad * detalle.precio_unitario, 2)
        
        # Recalcular total de la nota
        total_nota = session.query(func.sum(DetalleNotaVenta.subtotal)).filter_by(id_nota=id_nota).scalar() or 0
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if nota:
            nota.total = round(total_nota, 2)
        
        session.commit()
        print(f"Detalle del producto {id_producto} actualizado exitosamente")
        
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar detalle del producto: {e}")
        raise e
def agregar_detalle_nota(id_nota, id_producto, cantidad, precio_unitario, color, talla, subtotal):
    try:
        nuevo_detalle = DetalleNotaVenta(
            id_nota=id_nota,
            id_producto=id_producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            color=color,
            talla=talla,
            subtotal=subtotal
        )
        session.add(nuevo_detalle)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
def eliminar_detalle_nota(id_nota, id_producto):
    """
    Elimina un detalle de una nota de venta.
    :param id_nota: ID de la nota de venta.
    :param id_producto: ID del producto a eliminar del detalle.
    """
    try:
        # Buscar el detalle a eliminar
        detalle = session.query(DetalleNotaVenta).filter_by(id_nota=id_nota, id_producto=id_producto).first()
        if not detalle:
            raise ValueError("El detalle no existe en la nota de venta.")
        # Eliminar el detalle
        session.delete(detalle)
        # Recalcular el total de la nota
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if nota:
            nota.total -= detalle.subtotal  # Resta el subtotal del detalle eliminado
            session.commit()
            print(f"Detalle del producto ID {id_producto} eliminado de la nota de venta ID {id_nota}.")
        else:
            raise ValueError(Text_Nota_Venta)
    
    except Exception as e:
        session.rollback()
        raise ValueError(f"No se pudo eliminar el detalle de la nota de venta: {e}")
# Ganancias
def obtener_ventas_por_fecha(fecha_inicio, fecha_fin):
    # Cargamos las ventas canceladas con sus detalles en una sola consulta
    ventas = session.query(NotaVenta).filter(
        NotaVenta.estado == "Cancelado",
        NotaVenta.fecha_venta.between(fecha_inicio, fecha_fin)
    ).options(
        joinedload(NotaVenta.detalles).joinedload(DetalleNotaVenta.producto)  # Carga los detalles y productos en una sola consulta
    ).all()
    return ventas
def calcular_ganancia(ventas):
    return sum(
        (detalle.precio_unitario - detalle.producto.costo) * detalle.cantidad
        for venta in ventas
        for detalle in venta.detalles
    )
def calcular_total(ventas):
    return sum(
        detalle.precio_unitario * detalle.cantidad
        for venta in ventas
        for detalle in venta.detalles
    )
def calcular_costo_total(ventas):
    return sum(
        detalle.producto.costo * detalle.cantidad
        for venta in ventas
        for detalle in venta.detalles
    )
def obtener_productos_vendidos(ventas):
    return [
        {
            'producto': detalle.producto.nombre,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario,
            'subtotal': detalle.precio_unitario * detalle.cantidad,
            'costo': detalle.producto.costo
        }
        for venta in ventas
        for detalle in venta.detalles
    ]
def obtener_notas_filtradas(filtros_activos):
    query = session.query(
        NotaVenta.id_nota,
        NotaVenta.fecha_venta,
        NotaVenta.total,
        Cliente.nombre.label("nombre_cliente")  # Traer directamente el nombre del cliente
    ).join(Cliente, NotaVenta.id_cliente == Cliente.id_cliente, isouter=True).filter(NotaVenta.estado.ilike('%cancelado%'))
    if filtros_activos.get("ID Venta"):
        query = query.filter(cast(NotaVenta.id_nota, String).ilike(f"%{filtros_activos['ID Venta']}%"))
    if filtros_activos.get("Cliente"):
        query = query.filter(Cliente.nombre.ilike(f"%{filtros_activos['Cliente']}%"))
    if filtros_activos.get("Fecha Inicio"):
        query = query.filter(NotaVenta.fecha_venta >= filtros_activos["Fecha Inicio"])
    if filtros_activos.get("Fecha Fin"):
        query = query.filter(NotaVenta.fecha_venta <= filtros_activos["Fecha Fin"])
    return query.order_by(NotaVenta.fecha_venta.asc(), NotaVenta.id_nota.asc()).all()
def total_menos_amortizacion(id_nota):
    nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
    amortizaciones = session.query(Amortizacion).filter_by(id_nota=id_nota).all()
    total = nota.total
    for amortizacion in amortizaciones:
        total -= amortizacion.monto
    return total
def actualizar_estado_pedido(id_nota, nuevo_estado):
    try:
        nota = session.query(NotaVenta).filter_by(id_nota=id_nota).first()
        if not nota:
            raise ValueError(Text_Nota_Venta)
        
        nota.estado_pedido = nuevo_estado
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
def obtener_reporte(mes=None, anio=None, fecha_desde=None, fecha_hasta=None):
    q = (
        session.query(
            NotaVenta.id_nota.label("id_nota_venta"),
            Producto.nombre.label("producto"),
            Cliente.nombre.label("cliente"),
            DetalleNotaVenta.cantidad,
            DetalleNotaVenta.precio_unitario,
            NotaVenta.total.label("total_por_nota"),
            NotaVenta.fecha_venta
        )
        .select_from(NotaVenta)
        .join(DetalleNotaVenta, DetalleNotaVenta.id_nota == NotaVenta.id_nota)
        .join(Producto, Producto.id_producto == DetalleNotaVenta.id_producto)
        .join(Cliente, Cliente.id_cliente == NotaVenta.id_cliente)
    )
    # Filtro por rango de fechas si ambos están presentes
    if fecha_desde and fecha_hasta:
        q = q.filter(
            and_(
                NotaVenta.fecha_venta >= fecha_desde,
                NotaVenta.fecha_venta <= fecha_hasta
            )
        )
    # Si no hay rango, pero sí mes y año => construir rango del mes
    elif mes and anio:
        primer_dia = date(int(anio), int(mes), 1)
        ultimo_dia = date(int(anio), int(mes), monthrange(int(anio), int(mes))[1])
        q = q.filter(
            and_(
                NotaVenta.fecha_venta >= primer_dia,
                NotaVenta.fecha_venta <= ultimo_dia
            )
        )
    q = q.order_by(NotaVenta.fecha_venta, NotaVenta.id_nota)
    return q.all()