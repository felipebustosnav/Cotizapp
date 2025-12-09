-- Script para crear la base de datos CotizApp
-- Ejecutar este script en MySQL Workbench o desde la línea de comandos de MySQL

CREATE DATABASE IF NOT EXISTS cotizapp_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Seleccionar la base de datos
USE cotizapp_db;

-- Verificar que la base de datos fue creada
SHOW DATABASES LIKE 'cotizapp_db';

-- Después de ejecutar este script, ejecutar en el terminal:
-- python manage.py migrate
