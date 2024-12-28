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
    nombre_servicio varchar(20) not null UNIQUE,
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
    estado ENUM('pendiente','completado'),
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
    placa char(6),
    id_turno INT NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    total DOUBLE NOT NULL,
    CONSTRAINT fk_factura_cliente FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_factura_turno FOREIGN KEY (id_turno) REFERENCES turno (id_turno) 
        ON DELETE CASCADE ON UPDATE CASCADE
);
-- Tabla factura_no_cliente
CREATE TABLE IF NOT EXISTS factura_no_cliente (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    nombres varchar(30) not null,
    ci_ruc char(13) not null,
    fecha_hora TIMESTAMP NOT NULL,
    servicio varchar(30) not null,
    total DOUBLE NOT NULL
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
    id_admin int not null,
    nombre varchar(20) not null,
    descripcion VARCHAR(50) NOT NULL,
    total DOUBLE NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM ('pendiente','completado'),
    CONSTRAINT fk_admin_pedido FOREIGN KEY (id_admin) REFERENCES administrador (id_admin)
        ON DELETE CASCADE ON UPDATE CASCADE
);



DECLARE DELIMITER //
-- Procedimiento insertarProducto
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
END;

-- Trigger para registrar cambios al insertar un producto
CREATE TRIGGER registrar_cambios_producto
AFTER INSERT ON producto
FOR EACH ROW
BEGIN
    -- Registrar la inserción de un nuevo producto en la tabla historial
    INSERT INTO historial_producto(id_producto, nombre, descripcion, stock, precio, accion, fecha)
    VALUES (NEW.id_producto_inv, NEW.nombre, NEW.descripcion, NEW.stock, NEW.precio, 'INSERCION', NOW());
END;

-- Trigger para registrar cambios al actualizar un producto
CREATE TRIGGER registrar_cambios_producto_actualizacion
AFTER UPDATE ON producto
FOR EACH ROW
BEGIN
    -- Registrar la actualización del producto en la tabla historial
    INSERT INTO historial_producto(id_producto, nombre, descripcion, stock, precio, accion, fecha)
    VALUES (NEW.id_producto_inv, NEW.nombre, NEW.descripcion, NEW.stock, NEW.precio, 'ACTUALIZACION', NOW());
END;



-- Insert for trabajador
INSERT INTO trabajador (nombres, apellidos, cedula, contrato, fecha_contrato, salario)
VALUES ('Alcivar', 'Jostyn', '1234567890', '1', '2024-12-26', 500.00);

-- Insert for administrador
INSERT INTO administrador (id_trabajador, clave) 
VALUES (1, 'admin123');

