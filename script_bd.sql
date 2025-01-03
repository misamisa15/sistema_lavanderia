		DROP DATABASE IF EXISTS sistema_lavanderia;
		CREATE DATABASE sistema_lavanderia;

		USE sistema_lavanderia;

		-- Tabla cliente
		CREATE TABLE IF NOT EXISTS cliente (
			id_cliente INT AUTO_INCREMENT PRIMARY KEY,
			usuario_cliente varchar(20) not null UNIQUE,
			clave varchar(20) not null,
			nombres VARCHAR(20) NOT NULL,
			apellidos VARCHAR(20) NOT NULL,
			cedula CHAR(10) NOT NULL UNIQUE,
			ruc CHAR(13),
			telefono char(10) UNIQUE,
			vehiculo VARCHAR(40)
		);

		-- Tabla servicios
		CREATE TABLE IF NOT EXISTS servicio(
			id_servicio int AUTO_INCREMENT primary key,
			nombre_servicio varchar(20) not null,
			descripcion varchar(30),
			precio double not null,
			fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);

		-- Tabla turno
		CREATE TABLE IF NOT EXISTS turno (
			id_turno INT AUTO_INCREMENT PRIMARY KEY,
			id_cliente INT NOT NULL,
			tipo_servicio int not null,
			fecha_hora TIMESTAMP NOT NULL,
			CONSTRAINT fk_turn_cliente FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) 
				ON DELETE CASCADE ON UPDATE CASCADE,
			CONSTRAINT fk_turn_servicio FOREIGN KEY(tipo_servicio) REFERENCES servicio (id_servicio)
				ON DELETE CASCADE ON UPDATE CASCADE	
		);


		-- Tabla comprobante
		CREATE TABLE IF NOT EXISTS comprobante (
			id_comprobante INT AUTO_INCREMENT PRIMARY KEY,
			id_turno INT NOT NULL,
			fecha_hora TIMESTAMP NOT NULL,
			CONSTRAINT fk_comprobante_turno FOREIGN KEY (id_turno) REFERENCES turno (id_turno) 
				ON DELETE CASCADE ON UPDATE CASCADE
		);

		-- Tabla cuenta_por_cobrar
		CREATE TABLE IF NOT EXISTS cuenta_por_cobrar (
			id_cuenta_cobrar INT AUTO_INCREMENT PRIMARY KEY,
			id_cliente INT NOT NULL,
			id_turno INT NOT NULL,
			fecha_hora TIMESTAMP NOT NULL,
			total DOUBLE NOT NULL,
			CONSTRAINT fk_cuentaC_cliente FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) 
				ON DELETE CASCADE ON UPDATE CASCADE,
			CONSTRAINT fk_cuentaC_turno FOREIGN KEY (id_turno) REFERENCES turno (id_turno) 
				ON DELETE CASCADE ON UPDATE CASCADE
		);

		-- Tabla factura_cliente
		CREATE TABLE IF NOT EXISTS factura_cliente (
			id_factura INT AUTO_INCREMENT PRIMARY KEY,
			id_cliente INT NOT NULL,
			id_turno INT NOT NULL,
			fecha_hora TIMESTAMP NOT NULL,
			total DOUBLE NOT NULL,
			CONSTRAINT fk_factura_cliente FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) 
				ON DELETE CASCADE ON UPDATE CASCADE,
			CONSTRAINT fk_factura_turno FOREIGN KEY (id_turno) REFERENCES turno (id_turno) 
				ON DELETE CASCADE ON UPDATE CASCADE
		);

		-- Tabla producto
		CREATE TABLE IF NOT EXISTS producto (
			id_producto_inv INT AUTO_INCREMENT PRIMARY KEY,
			nombre VARCHAR(30) NOT NULL UNIQUE,
			descripcion VARCHAR(50) NOT NULL,
			stock INT NOT NULL,
			precio DOUBLE NOT NULL,
			fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);

		-- Crear la tabla historial_producto
		CREATE TABLE IF NOT EXISTS historial_producto (
			id_historial INT AUTO_INCREMENT PRIMARY KEY,
			id_producto INT,
			nombre VARCHAR(30),
			descripcion VARCHAR(50),
			stock INT,
			precio DOUBLE,
			accion ENUM('INSERCION', 'ACTUALIZACION'),
			fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);

		-- Tabla factura_producto
		CREATE TABLE IF NOT EXISTS factura_producto (
			id_factura_producto INT AUTO_INCREMENT PRIMARY KEY,
			id_factura INT NOT NULL,
			id_producto INT NOT NULL,
			cantidad INT NOT NULL,
			CONSTRAINT fk_producto_factura FOREIGN KEY (id_factura) REFERENCES factura_cliente (id_factura) 
				ON DELETE CASCADE ON UPDATE CASCADE,
			CONSTRAINT fk_facPro_Producto FOREIGN KEY (id_producto) REFERENCES producto (id_producto_inv) 
				ON DELETE CASCADE ON UPDATE CASCADE
		);

		-- Tabla trabajador
		CREATE TABLE IF NOT EXISTS trabajador (
			id_trabajador INT AUTO_INCREMENT PRIMARY KEY,
			nombres VARCHAR(20) NOT NULL,
			apellidos VARCHAR(20) NOT NULL,
			cedula CHAR(10) NOT NULL,
			contrato ENUM("1", "2", "3"),
			fecha_contrato TIMESTAMP NOT NULL,
			salario DOUBLE NOT NULL
		);

		-- Tabla administrador
		CREATE TABLE IF NOT EXISTS administrador (
			id_admin INT AUTO_INCREMENT PRIMARY KEY,
			id_trabajador INT NOT NULL,
			clave VARCHAR(16) NOT NULL,
			CONSTRAINT fk_administrador_trabajador FOREIGN KEY (id_trabajador) REFERENCES trabajador (id_trabajador) 
				ON DELETE CASCADE ON UPDATE CASCADE
		);

		-- Tabla pedido
		CREATE TABLE IF NOT EXISTS pedido (
			id_pedido INT AUTO_INCREMENT PRIMARY KEY,
			descripcion VARCHAR(50) NOT NULL,
			total DOUBLE NOT NULL
		);

		-- Tabla proveedor
		CREATE TABLE IF NOT EXISTS proveedor (
			id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
			nombres VARCHAR(20) NOT NULL,
			apellidos VARCHAR(20) NOT NULL,
			ruc CHAR(13) NOT NULL,
			empresa VARCHAR(20) NOT NULL
		);

		-- Tabla factura_proveedor
		CREATE TABLE IF NOT EXISTS factura_proveedor (
			id_fac_prov INT AUTO_INCREMENT PRIMARY KEY,
			id_proveedor INT NOT NULL,
			id_pedido INT NOT NULL,
			id_admin INT NOT NULL,
			codigo_factura CHAR(20) NOT NULL,
			total DOUBLE NOT NULL,
			CONSTRAINT fk_facprov_pedido FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido) 
				ON DELETE CASCADE ON UPDATE CASCADE,
			CONSTRAINT fk_facprov_admin FOREIGN KEY (id_admin) REFERENCES administrador (id_admin) 
				ON DELETE CASCADE ON UPDATE CASCADE,
			CONSTRAINT fk_facprov_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedor (id_proveedor) 
				ON DELETE CASCADE ON UPDATE CASCADE
		); 





		DELIMITER //
		CREATE PROCEDURE insertarProducto(
			IN p_nombre VARCHAR(30), 
			IN p_descripcion VARCHAR(50), 
			IN p_stock INT, 
			IN p_precio DOUBLE
		)
		BEGIN
			DECLARE v_producto_id INT;

			-- Verificar si el producto ya existe
			SELECT id_producto_inv INTO v_producto_id 
			FROM producto 
			WHERE nombre = p_nombre;

			IF v_producto_id IS NOT NULL THEN
				-- Si el producto existe, actualizar el stock
				UPDATE producto 
				SET stock = stock + p_stock 
				WHERE id_producto_inv = v_producto_id;
			ELSE
				-- Si el producto no existe, insertarlo
				INSERT INTO producto(nombre, descripcion, stock, precio) 
				VALUES (p_nombre, p_descripcion, p_stock, p_precio);
			END IF;
		END //
		DELIMITER ;

		-- Crear el trigger para registrar cambios
		DELIMITER //
		CREATE TRIGGER registrar_cambios_producto
		AFTER INSERT ON producto
		FOR EACH ROW
		BEGIN
			-- Registrar la inserción de un nuevo producto en la tabla historial
			INSERT INTO historial_producto(id_producto, nombre, descripcion, stock, precio, accion, fecha)
			VALUES (NEW.id_producto_inv, NEW.nombre, NEW.descripcion, NEW.stock, NEW.precio, 'INSERCION', NOW());
		END //

		CREATE TRIGGER registrar_cambios_producto_actualizacion
		AFTER UPDATE ON producto
		FOR EACH ROW
		BEGIN
			-- Registrar la actualización del producto en la tabla historial
			INSERT INTO historial_producto(id_producto, nombre, descripcion, stock, precio, accion, fecha)
			VALUES (NEW.id_producto_inv, NEW.nombre, NEW.descripcion, NEW.stock, NEW.precio, 'ACTUALIZACION', NOW());
		END //
		DELIMITER ;


		CALL insertarProducto("Rufles", "Papitas fritas rufles", 10, 0.50);
		
        
        
        
