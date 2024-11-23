----------------------------------------------------------------------------------------------
-- OJO: Este archivo solo es una guía para el mapeo de los modelos en el proyecto de django.--
----------------------------------------------------------------------------------------------

--
-- TABLA ROL
--
CREATE TABLE `Rol` (
    `id_rol` INT NOT NULL AUTO_INCREMENT UNIQUE,
    `nombre` VARCHAR(32) NOT NULL UNIQUE
);
-- Llave primaria tabla Rol --
ALTER TABLE `Rol`
ADD CONSTRAINT `pk_Rol`
PRIMARY KEY (`id_rol`);

--
-- TABLA USUARIO
--
CREATE TABLE `Usuario` (
    `id_usuario` INT NOT NULL AUTO_INCREMENT UNIQUE,
    `id_rol` INT NOT NULL,
    `nombre` VARCHAR(255) NOT NULL,
    `correo` VARCHAR(255) NOT NULL UNIQUE,
    `username` VARCHAR(64) NOT NULL UNIQUE,
    `password` VARCHAR(64) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- Llave primaria Usuario--
ALTER TABLE `Usuario`
ADD CONSTRAINT `pk_Usuario`
PRIMARY KEY (`id_usuario`);
-- Llave foranea Usuario --
ALTER TABLE `Usuario`
ADD CONSTRAINT `fk_Usuario`
FOREIGN KEY (`id_rol`)
REFERENCES `Rol`(`id_rol`)
ON DELETE CASCADE
ON UPDATE CASCADE;

--
-- TABLA COMIC
--
CREATE TABLE `Comic` (
    `id_comic` INT NOT NULL AUTO_INCREMENT UNIQUE,
    `id_vendedor` INT NOT NULL,
    `nombre` VARCHAR(255) NOT NULL,
    `descripcion` TEXT DEFAULT NULL,
    `ruta_imagen` TEXT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- Llave primaria Comic --
ALTER TABLE `Comic`
ADD CONSTRAINT `pk_Comic`
PRIMARY KEY (`id_comic`);
-- Llave foranea Comic --
ALTER TABLE `Comic`
ADD CONSTRAINT `fk_Comic`
FOREIGN KEY (`id_vendedor`)
REFERENCES `Usuario`(`id_usuario`)
ON DELETE CASCADE
ON UPDATE CASCADE;

--
-- TABLA OFERTA
--
CREATE TABLE `Oferta` (
    `id_oferta` INT NOT NULL AUTO_INCREMENT UNIQUE,
    `id_emisor` INT NO NULL, -- Comprador
    `id_receptor` INT NOT NULL, -- Vendedor
    `objeto` VARCHAR(255) NOT NULL,
    `descripcion` TEXT DEFAULT NULL,
    `servicio` BOOLEAN NOT NULL DEFAULT FALSE,
    `aceptada` BOOLEAN DEFAULT NULL,
    `visto` BOOLEAN NOT NULL DEFAULT FALSE,
    `ruta_imagen` TEXT NOT NULL,    
    `fecha_emision` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- Llave primaria Oferta --
ALTER TABLE `Oferta`
ADD CONSTRAINT `pk_Oferta`
PRIMARY KEY (`id_oferta`);
-- Llave foranea Emisor --
ALTER TABLE `Oferta`
ADD CONSTRAINT `fk_emisor`
FOREIGN KEY (`id_emisor`)
REFERENCES `Usuario`(`id_usuario`)
ON DELETE CASCADE
ON UPDATE CASCADE;
-- Llave foranea Remitente --
ALTER TABLE `Oferta`
ADD CONSTRAINT `fk_receptor`
FOREIGN KEY (`id_receptor`)
REFERENCES `Usuario`(`id_usuario`)
ON DELETE CASCADE
ON UPDATE CASCADE;

--
-- Tabla Mensaje
--
CREATE TABLE `Mensaje` (
    `id_mensaje` INT NOT NULL AUTO_INCREMENT UNIQUE,
    `id_emisor` INT NOT NULL,
    `id_receptor` INT NOT NULL,
    `fecha_emision` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `visto` BOOLEAN NOT NULL DEFAULT FALSE
);
-- Llave primaria Mensaje --
ALTER TABLE `Mensaje`
ADD CONSTRAINT `pk_Mensaje`
PRIMARY KEY (`id_mensaje`);
-- Llave foranea Emisor --
ALTER TABLE `Mensaje`
ADD CONSTRAINT `fk_emisor`
FOREIGN KEY (`id_emisor`)
REFERENCES `Usuario`(`id_usuario`)
ON DELETE CASCADE
ON UPDATE CASCADE;
-- Llave foranea Emisor --
ALTER TABLE `Mensaje`
ADD CONSTRAINT `fk_receptor`
FOREIGN KEY (`id_receptor`)
REFERENCES `Usuario`(`id_usuario`)
ON DELETE CASCADE
ON UPDATE CASCADE;
