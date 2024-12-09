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
        {'icon': 'person', 'text': 'Clientes'},
        {'icon': 'database', 'text': 'Produc/Servicios'},
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
        # Devuelve los datos del primer cliente como JSON
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

products = [
    {'name': 'Producto 1', 'description': 'Descripción del Producto 1', 'price': 10.0},
    {'name': 'Producto 2', 'description': 'Descripción del Producto 2', 'price': 15.5},
    # Agrega más productos si deseas
]

@app.route('/inicio_sesion.html')
def inicioSesion():


    return render_template('pg_iniciosesion.html')

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

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    # Lista de clientes (en este caso, lista simulada, puedes cambiarla por una base de datos)
    clientes = [
        {'cedula': '1234567890', 'nombres': 'Juan Pérez', 'telefono': '0987654321', 'correo': 'juan@example.com'},
        {'cedula': '0987654321', 'nombres': 'María López', 'telefono': '0981234567', 'correo': 'maria@example.com'},
    ]

    if request.method == 'POST':
        # Obtener datos del formulario
        cedula = request.form.get('cedula')
        nombres = request.form.get('nombres')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        
        # Agregar nuevo cliente a la lista (o base de datos)
        clientes.append({'cedula': cedula, 'nombres': nombres, 'telefono': telefono, 'correo': correo})
        
        # Redirigir a la misma página para actualizar la lista
        return redirect(url_for('clientes'))
    
    # Renderizar la plantilla de clientes
    return render_template('clientes.html', clientes=clientes)
