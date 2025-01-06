from flask import Flask, abort, jsonify, render_template, current_app as app, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import url_for,redirect
from flask import Flask,render_template, request
from flask_mysqldb import MySQL 
from datetime import datetime
from flask_mysqldb import MySQL


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'sistema_lavanderia'
mysql = MySQL(app)
cursor = mysql.connection.cursor()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('paguser'))

@app.context_processor
def inject_menu():
    menu = [
        {'text': 'Inicio', 'url': '/pagina_user.html'},
        {'text': 'Turnos', 'url': '/turnos.html'},
        {'text': 'Servicios', 'url': '/user_servicios.html'},
        {'text': 'Compras', 'url': '/user_productos.html'},
        {'text': 'Facturas', 'url': '/user_facturas.html'},
    ]
    if session.get('logged_in'):
        opciones = [
            {'text': 'Cerrar Sesión', 'url': '/logout'}
        ]
    else:
        opciones = [
            {'text': 'Iniciar Sesión', 'url': '/inicio_sesion.html'},
            {'text': 'Registrarse', 'url': '/registro.html'}
        ]
    
    return dict(
        menu=menu,
        opciones=opciones,
        user_name=session.get('user_name')
    )

#Logica de las interfaces de usuario
@app.route('/pagina_user.html')
def paguser():
    
    ima = [
        
        {'image': 'images/logo_lavadora.png'},
        {'image': 'images/imagen_horario_car.jpeg'},
        {'image': 'images/publi_lava.jpg'}
    ]
    return render_template('pagina_user.html', ima=ima)


@app.route('/turnos.html')
def pagturnos():
    cursor=mysql.connection.cursor()
    query="Select nombre_servicio from servicio;"
    cursor.execute(query)
    servicios=cursor.fetchall()
    return render_template('turnos.html',servicios=servicios)

@app.route('/turnoAgregar', methods=['POST'])
def agregar_turno():
    data = request.json
    id_cliente = session.get('user_id')
    servicio = data.get('servicio')
    fecha = data.get('fecha')
    hora = data.get('hora')
    
    fechahora = f"{fecha} {hora}"  
    
    cursor = mysql.connection.cursor()
    query_check = "SELECT COUNT(*) FROM turno WHERE fecha_hora = %s;"
    cursor.execute(query_check, (fechahora,))
    count = cursor.fetchone()[0]
    
    if count >= 3:
        cursor.close()
        return jsonify({"error": "No se puede agendar el turno. Ya hay 3 turnos registrados en esa fecha y hora."}), 400
    
    query_insert = "INSERT INTO turno (id_cliente, tipo_servicio, fecha_hora,estado) VALUES (%s, %s, %s,'pendiente');"
    cursor.execute(query_insert, (id_cliente, servicio, fechahora))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({"message": "Turno registrado con éxito."}), 200

@app.route('/user_productos.html')
def user_producto():

    cursor = mysql.connection.cursor()
    query="Select nombre,descripcion, precio from producto where stock > 0;"
    cursor.execute(query)
    productos = cursor.fetchall()      
    cursor.close()

    return render_template('pg_productos_user.html', productos=productos)
    

@app.route('/user_servicios.html', methods=['GET', 'POST'])
def produc_servicios():

    cursor = mysql.connection.cursor()
    query="Select nombre_servicio,descripcion, precio from servicio;"
    cursor.execute(query)
    servicios = cursor.fetchall()      
    cursor.close()

    return render_template('pg_servicios_user.html', servicios=servicios)


# Registro e inicio de sesión

@app.route('/registro.html')
def registro():
    return render_template('registro.html')

@app.route('/registroUsuario', methods=['POST'])
def nuevoUsuario():
    data=request.json
    usuario=data.get('user')
    clave=data.get('pass')
    nombres=data.get('nombre')
    apellidos=data.get('apellido')
    cedula=data.get('cedula')
    ruc=data.get('ruc')
    telefono=data.get('telefono')
    vehiculo=data.get('vehiculo')
    cursor= mysql.connection.cursor()
    banderaUser=True
    banderaCed=True
    banderaRuc=True
    banderaTel=True
    
    query="Select * from cliente where usuario_cliente = %s;"
    cursor.execute(query,(usuario,))
    nom_usuario = cursor.fetchone()
    if nom_usuario:
        banderaUser=False
        return jsonify({"error": "Hay usuario registrado con ese username."}), 404


    query="Select * from cliente where cedula = %s;"
    cursor.execute(query,(cedula,))
    ced_usuario = cursor.fetchone()
    if ced_usuario:
        banderaCed=False
        return jsonify({"error": "Hay usuario registrado con esa cedula."}), 404
    
    if ruc and ruc.strip():  
        query = "SELECT * FROM cliente WHERE ruc = %s;"
        cursor.execute(query, (ruc,))
        ruc_usuario = cursor.fetchone()
        if ruc_usuario:
            banderaRuc = False
            return jsonify({"error": "Hay usuario registrado con ese ruc."}), 404
    
    query="Select * from cliente where telefono = %s;"
    cursor.execute(query,(telefono,))
    tel_usuario = cursor.fetchone()
    if tel_usuario:
        banderaTel=False
        return jsonify({"error": "Hay usuario registrado con ese número de telefono."}), 404

    
    if banderaUser==True & banderaCed==True & banderaRuc==True &banderaTel==True:
        query="insert into cliente (usuario_cliente,clave, nombres, apellidos,cedula,ruc,telefono,vehiculo) values(%s,%s,%s,%s,%s,%s,%s,%s);"
        cursor.execute(query,(usuario,clave,nombres,apellidos,cedula,ruc,telefono,vehiculo))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Se ha registrado con éxito."}), 200


@app.route('/inicio_sesion.html')
def inicioSesion():
    return render_template('pg_iniciosesion.html')

@app.route('/inicioSesion', methods=['POST'])
def iniciarSesion():
    data = request.json
    usuario = data.get('user')
    clave = data.get('pass')
    
    cursor = mysql.connection.cursor()
    query = "SELECT id_cliente, usuario_cliente, nombres, apellidos, cedula, ruc, vehiculo FROM cliente WHERE usuario_cliente = %s AND clave = %s;"
    cursor.execute(query,(usuario,clave,))
    cliente_infor = cursor.fetchone()
    cursor.close()
    
    if cliente_infor:
        nombre_inicial = cliente_infor[2][0].upper() if cliente_infor[2] else ''
        apellido_inicial = cliente_infor[3][0].upper() if cliente_infor[3] else ''
        
        # Guardar información en la sesión
        session['user_id'] = cliente_infor[0]
        session['user_cedula']=cliente_infor[4]
        session['user_name'] = f"{nombre_inicial}{apellido_inicial}"
        session['logged_in'] = True
        
        return jsonify({
            "id_cliente": cliente_infor[0],
            "nombres": cliente_infor[2],
            "apellidos": cliente_infor[3],
            "cedula": cliente_infor[4],
            "ruc": cliente_infor[5],
            "vehiculo": cliente_infor[6]
        })
    else:
        return jsonify({"error": "Credenciales no validas."}), 404

#Logica de las interfaces de administración

@app.route('/')
def index():
    buttons = [
        {'icon': 'person', 'text': 'Clientes', 'url':'/cliente.html'},
        {'icon': 'database', 'text': 'Productos', 'url':'/productos.html'},
        {'icon': 'file-earmark-check', 'text': 'Servicios','url':'/servicios.html'},
        {'icon': 'file-earmark-check', 'text': 'Nueva Factura'},
        {'icon': 'receipt', 'text': 'Comprobantes'},
        {'icon': 'receipt-cutoff', 'text': 'Ver turnos próximos','url':'/pg_turnos.html'},
        {'icon': 'journal-text', 'text': 'Lista Retenciones'},
        {'icon': 'arrow-clockwise', 'text': 'Nota de Crédito'},
        {'icon': 'file-earmark-minus', 'text': 'Administrar Pedidos','url':'/pedidos.html'},
        {'icon': 'journal-text', 'text': 'Ver Pedidos', 'url':'/ver_pedidos.html'},
        {'icon': 'file-earmark-text', 'text': 'Proformas'},
        {'icon': 'cash-stack', 'text': 'Cuentas por Cobrar'},
    ]
    
    return render_template('pagina_principal.html', buttons=buttons)

@app.route('/pg_turnos.html')
def verTurnos():
    cursor=mysql.connection.cursor()
    query="Select tur.id_turno, cl.nombres, cl.apellidos,cedula,ser.nombre_servicio, ser.precio,tur.fecha_hora from turno as tur inner join cliente  cl on cl.id_cliente=tur.id_cliente inner join servicio as ser on ser.id_servicio=tur.tipo_servicio where DATE(tur.fecha_hora) >= CURDATE() AND estado='pendiente'  order by tur.fecha_hora asc;"
    cursor.execute(query)
    turnos=cursor.fetchall()
    cursor.close()
    return render_template('pg_turnos.html',turnos=turnos)

@app.route('/ver_pedidos.html', methods=['GET', 'POST'])
def verpedidos():
    cursor=mysql.connection.cursor()
    query="Select id_pedido,nombre,descripcion,total, fecha, estado from pedido where estado='pendiente';"
    cursor.execute(query)
    pendientes=cursor.fetchall()
    query="Select id_pedido,nombre,descripcion,total, fecha, estado from pedido where estado='completado';"
    cursor.execute(query)
    completados=cursor.fetchall()
    cursor.close()
    return render_template('pg_ver_pedidos.html', pedidos_pendientes=pendientes,pedidos_completados=completados)

@app.route('/pedidos.html')
def generarPedido():

    return render_template('pg_pedidos.html')

@app.route('/pedido', methods =['POST'])
def registrarpedido():
    data =request.json
    nombre=data.get('nombre')
    descripcion=data.get('descripcion')
    valor=data.get('precio')

    cursor=mysql.connection.cursor()
    query="INSERT INTO pedido (id_admin,nombre,descripcion,total,estado) values (1,%s,%s,%s, 'pendiente');"
    cursor.execute(query,(nombre,descripcion,valor))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Pedido agregado con éxito"}), 200

@app.route('/pedidoBuscar',methods=['POST'])
def buscarpedido():
    data=request.json
    nombre=data.get('nombre')
    cursor=mysql.connection.cursor()
    query="SELECT id_pedido,nombre, descripcion,total,fecha,estado from pedido where nombre=%s;"
    cursor.execute(query,(nombre,))
    pedido=cursor.fetchone()
    cursor.close()

    if pedido:
        return jsonify({
            "id_pedido":pedido[0],
            "nombre":pedido[1],
            "descripcion":pedido[2],
            "total":pedido[3],
            "fecha":pedido[4],
            "estado":pedido[5]
        })

@app.route('/eliminarPedido/<int:id_pedido>', methods=['DELETE'])
def eliminar_pedido(id_pedido):
    cursor = mysql.connection.cursor()
    query = "DELETE FROM pedido WHERE id_pedido = %s"
    cursor.execute(query, (id_pedido,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Pedido eliminado correctamente"}), 200

@app.route('/completarPedido/<int:id_pedido>', methods=['PUT'])
def completar_pedido(id_pedido):
    cursor = mysql.connection.cursor()
    query = "UPDATE pedido SET estado = 'completado' WHERE id_pedido = %s"
    cursor.execute(query, (id_pedido,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Pedido marcado como completado"}), 200
    
        
@app.route('/cliente.html')
def pagcli():
    return render_template('cliente.html')

@app.route('/cliente', methods=['POST'])
def buscar_cliente():
    data = request.json 
    cedula = data.get('cedula')

    cursor = mysql.connection.cursor()
    # Modificamos la consulta para obtener el primer cliente registrado
    query = "SELECT id_cliente, nombres, apellidos,cedula, ruc, vehiculo FROM cliente where cedula = %s;"  
    cursor.execute(query,(cedula,))
    cliente = cursor.fetchone() 
    cursor.close()

    if cliente:
        return jsonify({
            "id_cliente": cliente[0],
            "nombres": cliente[1],
            "apellidos": cliente[2],
            "cedula": cliente[3],
            "ruc":cliente[4],
            "vehiculo": cliente[5]
        })
    


@app.route('/productos.html')
def pagpro():
    return render_template('pg_productos.html')

@app.route('/producto', methods=['POST'])
def buscar_producto():
    data = request.json 
    nom = data.get('nombre')

    cursor = mysql.connection.cursor()
    query = "SELECT id_producto_inv, nombre, descripcion,stock, precio, fecha FROM producto where nombre = %s;"  
    cursor.execute(query,(nom,))
    producto = cursor.fetchone()  
    cursor.close()

    if producto:
        return jsonify({
            "id_producto_inv": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "stock": producto[3],
            "precio":producto[4],
            "fecha":producto[5]
        })
    else:
        return jsonify({"error": "No hay productos registrados"}), 404

@app.route('/producto/agregar-actualizar', methods=['POST'])
def agregar_actualizar_producto():
    data = request.json
    nom = data.get('nombre')
    desc = data.get('descripcion')
    stock = data.get('stock')
    precio = data.get('precio') 

    cursor = mysql.connection.cursor()
    query = "CALL insertarProducto(%s, %s, %s, %s)"  
    cursor.execute(query, (nom, desc, stock, precio))
    mysql.connection.commit()  
    cursor.close()
    return jsonify({"message": "Producto agregado o actualizado con éxito"}), 200


@app.route('/servicios.html')
def pagser():
    return render_template('pg_servicios.html')

@app.route('/servicios', methods=['POST'])
def buscar_servicio():
    data = request.json 
    nom = data.get('nombre')

    cursor = mysql.connection.cursor()
 
    query = "SELECT id_servicio, nombre_servicio, descripcion, precio, fecha_creacion FROM servicio where nombre_servicio = %s;"  
    cursor.execute(query,(nom,))
    producto = cursor.fetchone() 
    cursor.close()

    if producto:
        return jsonify({
            "id_servicio": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "precio":producto[3],
            "fecha":producto[4]
        })
    else:
        return jsonify({"error": "No hay servicio registrado"}), 404

@app.route('/servicioAgregar',methods=['POST'])
def servicio_agre_act():
    data = request.json
    nom = data.get('nombre')
    desc = data.get('descripcion')
    precio = data.get('precio') 
# Validar datos
    if not nom or not desc or precio is None or not isinstance(precio, (int, float)):
            return jsonify({"error": "Datos inválidos"}), 400
    cursor = mysql.connection.cursor()
    query = "INSERT INTO servicio(nombre_servicio,descripcion, precio)values(%s, %s, %s)"  
    cursor.execute(query, (nom, desc, precio))
    mysql.connection.commit()  
    cursor.close()
    return jsonify({"message": "Servicio agregado con éxito"}), 200

@app.route('/factura', methods=['GET'])
def mostrar_formulario():
    # Consultar el próximo número de factura dinámicamente
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT IFNULL(MAX(id_factura), 0) + 1 AS siguiente_factura FROM factura_no_cliente")
    resultado = cursor.fetchone()
    siguiente_factura = resultado[0] if resultado else 1  # Si no hay datos, iniciar en 1
    return render_template('factura.html', id_factura=siguiente_factura)

# Ruta para generar la factura
@app.route('/generar-factura', methods=['POST'])
def generar_factura():
    # Obtener los datos del formulario
    id_factura = request.form.get('id_factura')
    nombres = request.form['nombres']
    ci_ruc = request.form['ci_ruc']
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora actual
    servicio = request.form['servicio']
    total = request.form['total']

    # Guardar los datos en la base de datos
    cursor = mysql.connection.cursor()
    query = """
        INSERT INTO factura_no_cliente (id_factura, nombres, ci_ruc, fecha_hora, servicio, total)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (id_factura, nombres, ci_ruc, fecha_hora, servicio, total))
    mysql.connection.commit()

    # Renderizar la página con los datos generados
    return render_template(
        'factura_generada.html',
        id_factura=id_factura,
        nombres=nombres,
        ci_ruc=ci_ruc,
        fecha_hora=fecha_hora,
        servicio=servicio,
        total=total
    )
    
@app.route('/comprobantes', methods=['GET'])
def ver_comprobantes():
    # Consultar todas las facturas en la base de datos
    cursor = mysql.connection.cursor()
    query = "SELECT id_factura, nombres, ci_ruc, fecha_hora, servicio, total FROM factura_no_cliente"
    cursor.execute(query)
    facturas = cursor.fetchall()  # Recupera todas las filas como lista de tuplas

    # Convertir las filas a una estructura más legible si es necesario
    facturas_lista = [
        {
            "id_factura": factura[0],
            "nombres": factura[1],
            "ci_ruc": factura[2],
            "fecha_hora": factura[3],
            "servicio": factura[4],
            "total": factura[5]
        }
        for factura in facturas
    ]

    # Renderizar la plantilla con los datos de las facturas
    return render_template('comprobantes.html', facturas=facturas_lista)

@app.route('/imprimir/<int:id_factura>', methods=['GET'])
def imprimir_factura(id_factura):
    # Consultar la factura específica por ID
    cursor = mysql.connection.cursor()
    query = "SELECT id_factura, nombres, ci_ruc, fecha_hora, servicio, total FROM factura_no_cliente WHERE id_factura = %s"
    cursor.execute(query, (id_factura,))
    factura = cursor.fetchone()

    # Verificar si la factura existe
    if not factura:
        return "Factura no encontrada", 404

    # Convertir la factura en un diccionario para facilitar el uso
    factura_dict = {
        "id_factura": factura[0],
        "nombres": factura[1],
        "ci_ruc": factura[2],
        "fecha_hora": factura[3],
        "servicio": factura[4],
        "total": factura[5]
    }

    # Renderizar la plantilla imprimible
    return render_template('imprimir_factura.html', factura=factura_dict)
