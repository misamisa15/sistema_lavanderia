from flask import Flask, abort, jsonify, render_template, current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,render_template, request
from flask_mysqldb import MySQL # type: ignore


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'sistema_lavanderia'
mysql = MySQL(app)

cursor = mysql.connection.cursor()


@app.route('/')
def index():
    buttons = [
        {'icon': 'person', 'text': 'Clientes', 'url':'/cliente.html'},
        {'icon': 'database', 'text': 'Produc/Servicios', 'url':'/productos.html'},
        {'icon': 'file-earmark-check', 'text': 'Nueva Factura'},
        {'icon': 'receipt', 'text': 'Comprobantes'},
        {'icon': 'receipt-cutoff', 'text': 'Nueva Retención'},
        {'icon': 'journal-text', 'text': 'Lista Retenciones'},
        {'icon': 'arrow-clockwise', 'text': 'Nota de Crédito'},
        {'icon': 'file-earmark-minus', 'text': 'Nota de Débito'},
        {'icon': 'journal-album', 'text': 'Liquidación de Compras'},
        {'icon': 'file-earmark-text', 'text': 'Proformas'},
        {'icon': 'cash-stack', 'text': 'Cuentas por Cobrar'}
    ]
    
    return render_template('pagina_principal.html', buttons=buttons)


@app.route('/productos.html')
def pagpro():
    return render_template('pg_productos.html')

@app.route('/producto', methods=['POST'])
def buscar_producto():
    data = request.json 
    nom = data.get('nombre')

    cursor = mysql.connection.cursor()
    # Modificamos la consulta para obtener el producto registrado
    query = "SELECT id_producto_inv, nombre, descripcion,stock, precio, fecha FROM producto where nombre = %s;"  
    cursor.execute(query,(nom,))
    producto = cursor.fetchone()  # Obtiene la primera fila 
    cursor.close()

    if producto:
        # Devuelve los datos del primer producto como JSON
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
    # Obtener los datos del JSON recibido
    data = request.json
    nom = data.get('nombre')
    desc = data.get('descripcion')
    stock = data.get('stock')
    precio = data.get('precio')  # Corregir la variable 'precio'

    # Ejecutar el procedimiento almacenado en MySQL
    cursor = mysql.connection.cursor()
    query = "CALL insertarProducto(%s, %s, %s, %s)"  # Eliminar la coma extra
    cursor.execute(query, (nom, desc, stock, precio))
    mysql.connection.commit()  # Asegurarse de guardar los cambios en la base de datos
    cursor.close()

    # Devolver una respuesta al cliente
    return jsonify({"message": "Producto agregado o actualizado con éxito"}), 200


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
    cliente = cursor.fetchone()  # Obtiene la primera fila (primer cliente)
    cursor.close()

    if cliente:
        # Devuelve los datos del primer cliente como JSON
        return jsonify({
            "id_cliente": cliente[0],
            "nombres": cliente[1],
            "apellidos": cliente[2],
            "cedula": cliente[3],
            "ruc":cliente[4],
            "vehiculo": cliente[5]
        })
    else:
        return jsonify({"error": "No hay clientes registrados"}), 404


@app.route('/pagina_user.html')
def paguser():
    menu = [
        {'text': 'Inicio','link':'/pagina_user'},
        {'text': 'Turnos', 'link': '/turnos'},
        {'text': 'Servicios'},
        {'text': 'Compras'},
        {'text': 'Facturas'}
    ]
    ima = [
        
        {'image': 'images/logo_lavadora.png'},
        {'image': 'images/imagen_horario_car.jpeg'},
        {'image': 'images/publi_lava.jpg'}
    ]


    return render_template('pagina_user.html',menu=menu, ima=ima)


@app.route('/turnos.html')
def pagturnos():
    menu = [
        {'text': 'Inicio','link':'/pagina_user'},
        {'text': 'Turnos', 'link': '/turnos'},
        {'text': 'Servicios'},
        {'text': 'Compras'},
        {'text': 'Facturas'}
    ]
    ima = [
        
        {'image': 'images/logo_lava.jpg'},
        {'image': 'images/imagen_horario_car.jpeg'},
        {'image': 'images/publi_lava.jpg'}
    ]


    return render_template('turnos.html',menu=menu, ima=ima)

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
    
    if ruc and ruc.strip():  # Verifica si ruc no es None y no está vacío
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
    clave= data.get('pass')

    cursor = mysql.connection.cursor()

    query = "SELECT id_cliente, usuario_cliente, nombres, apellidos, cedula, ruc, vehiculo FROM cliente WHERE usuario_cliente = %s AND clave = %s;"  
    cursor.execute(query,(usuario,clave,))
    cliente_infor = cursor.fetchone()  # Obtiene la primera fila 
    cursor.close()

    if cliente_infor:
        # Devuelve los datos del primer cliente como JSON
        return jsonify({
            "id_cliente": cliente_infor[0],
            "nombres": cliente_infor[2],
            "apellidos": cliente_infor[3],
            "cedula": cliente_infor[4],
            "ruc":cliente_infor[5],
            "vehiculo":cliente_infor[6]
        })
    else:
        return jsonify({"error": "Credenciales no validas."}), 404


@app.route('/user_productos.html', methods=['GET', 'POST'])
def produc_servicios():

    menu = [
        {'text': 'Inicio','link':'/pagina_user'},
        {'text': 'Turnos', 'link': '/turnos'},
        {'text': 'Servicios'},
        {'text': 'Compras'},
        {'text': 'Facturas'}
    ]
    ima = [
        
        {'image': 'images/logo_lava.jpg'},
        {'image': 'images/imagen_horario_car.jpeg'},
        {'image': 'images/publi_lava.jpg'}
    ]
    if request.method == 'POST':
        # Recibir datos del formulario
        product_name = request.form.get('product_name')
        product_description = request.form.get('product_description')
        
        # Añadir el producto a la lista o base de datos
        products.append({'name': product_name, 'description': product_description})
        
        # Redirigir a la misma página después de añadir el producto
        return redirect(url_for('/user_productos.html'),menu=menu, ima=ima)
    
    # Renderizar la plantilla de productos
    return render_template('produc_servicios.html' ,menu=menu, ima=ima)
