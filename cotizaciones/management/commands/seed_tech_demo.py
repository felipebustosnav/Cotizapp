import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from empresas.models import Empresa
from usuarios.models import Usuario
from clientes.models import Cliente
from productos.models import Producto
from cotizaciones.models import Cotizacion, DetalleCotizacion, ReglaOfertaAutomatica
from impuestos.models import Impuesto, ProductoImpuesto

User = get_user_model()

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos ficticios de una empresa tecnológica para demo'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando generación de datos de prueba...'))

        # 1. Crear Empresa
        empresa, created = Empresa.objects.get_or_create(
            rut='76.543.210-K',
            defaults={
                'nombre': 'TechNova Solutions',
                'direccion': 'Av. Providencia 1234, Of 601, Santiago',
                'telefono': '+56912345678',
                'email': 'contacto@technova.cl',
                'mensaje_autoatencion': 'Bienvenido al portal de autogestión de TechNova. Aquí podrás solicitar cotizaciones de nuestros servicios cloud y hardware.',
                'mensaje_correo_cotizacion': 'Estimado cliente, adjuntamos la propuesta técnica y económica solicitada. Atentamente, equipo TechNova.',
                'mensaje_whatsapp_cotizacion': 'Hola! 🚀 Tu cotización TechNova está lista. Revísala aquí:',
                'autoaprobar_cotizaciones': True,
                'mensajeria_automatica_activa': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Empresa creada: {empresa.nombre}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Usando empresa existente: {empresa.nombre}'))

        # 2. Crear Usuarios
        # Admin
        admin, _ = Usuario.objects.get_or_create(
            email='admin@technova.cl',
            defaults={
                'username': 'admin@technova.cl',
                'first_name': 'Roberto',
                'last_name': 'CEO',
                'rol': Usuario.Rol.ADMINISTRADOR,
                'empresa': empresa
            }
        )
        if _:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin creado: admin@technova.cl / admin123'))

        # Empleados
        vendedores = []
        nombres_vendedores = [
            ('Camila', 'Ventas', 'camila@technova.cl'),
            ('Javier', 'Ejecutivo', 'javier@technova.cl')
        ]
        
        for name, last, mail in nombres_vendedores:
            vendedor, _ = Usuario.objects.get_or_create(
                email=mail,
                defaults={
                    'username': mail,
                    'first_name': name,
                    'last_name': last,
                    'rol': Usuario.Rol.EMPLEADO,
                    'empresa': empresa
                }
            )
            if _:
                vendedor.set_password('vendedor123')
                vendedor.save()
            vendedores.append(vendedor)
        self.stdout.write(self.style.SUCCESS(f'{len(vendedores)} vendedores verificados.'))

        # 3. Impuesto IVA
        iva, _ = Impuesto.objects.get_or_create(
            nombre='IVA',
            empresa=empresa,
            defaults={'porcentaje': 19.00, 'activo': True}
        )

        # 4. Productos Tecnológicos
        productos_data = [
            # Hardware
            ('Laptop Dev Pro X1', 'Ultrabook i7 32GB RAM 1TB SSD', 'HW-LPX1', 'Hardware', 'TechBrand', 1250000),
            ('Monitor 4K UltraWide', 'Monitor 34 pulgadas curvo para productividad', 'HW-M4K', 'Hardware', 'ViewMax', 450000),
            ('Servidor Rack Gen10', 'Servidor empresarial 2x Xeon 128GB RAM', 'HW-SRV10', 'Hardware', 'ServerKing', 3500000),
            # Software/Licencias
            ('Licencia Cloud ERP (Anual)', 'Suscripción anual sistema ERP módulo finanzas', 'SW-ERP-Y', 'Software', 'SoftCorp', 850000),
            ('Office Suite Business', 'Licencia perpetua paquete ofimática', 'SW-OFF', 'Software', 'MS', 180000),
            ('Antivirus Enterprise Endpoint', 'Protección endpoint gestionada (precio por nodo)', 'SW-AV-E', 'Software', 'SecureNet', 25000),
            # Servicios
            ('Hora Consultoría TI', 'Hora de ingeniero senior para implementaciones', 'SRV-CONS', 'Servicios', 'TechNova', 65000),
            ('Soporte Mensual 24/7', 'Plan de soporte nivel 2 con SLA 4 horas', 'SRV-SOP-M', 'Servicios', 'TechNova', 350000),
            ('Instalación y Configuración', 'Servicio de puesta en marcha servidor/red', 'SRV-INST', 'Servicios', 'TechNova', 150000),
        ]

        productos = []
        for nombre, desc, sku, tipo, marca, precio in productos_data:
            prod, _ = Producto.objects.get_or_create(
                sku=sku,
                empresa=empresa,
                defaults={
                    'nombre': nombre,
                    'descripcion': desc,
                    'tipo': tipo,
                    'marca': marca,
                    'precio': precio,
                    'activo': True
                }
            )
            # Asignar IVA
            ProductoImpuesto.objects.get_or_create(producto=prod, impuesto=iva)
            productos.append(prod)
        
        self.stdout.write(self.style.SUCCESS(f'{len(productos)} productos creados/verificados.'))

        # 5. Reglas de Oferta Automática
        ReglaOfertaAutomatica.objects.get_or_create(
            empresa=empresa,
            orden=1,
            defaults={
                'tiempo_espera_valor': 24,
                'tiempo_espera_unidad': ReglaOfertaAutomatica.UnidadTiempo.HORAS,
                'descuento_porcentaje': 5,
                'tiempo_validez_valor': 3,
                'tiempo_validez_unidad': ReglaOfertaAutomatica.UnidadTiempo.DIAS
            }
        )
        ReglaOfertaAutomatica.objects.get_or_create(
            empresa=empresa,
            orden=2,
            defaults={
                'tiempo_espera_valor': 3,
                'tiempo_espera_unidad': ReglaOfertaAutomatica.UnidadTiempo.DIAS,
                'descuento_porcentaje': 10,
                'tiempo_validez_valor': 2,
                'tiempo_validez_unidad': ReglaOfertaAutomatica.UnidadTiempo.DIAS
            }
        )
        self.stdout.write(self.style.SUCCESS('Reglas de oferta automática configuradas.'))

        # 6. Clientes y Cotizaciones - Generación Histórica (90 días)
        clientes_fake = [
            ('Constructora Los Andes', '77.111.222-3', 'const@losandes.cl'),
            ('Colegio San Ignacio', '65.333.444-5', 'admin@sanignacio.cl'),
            ('Distribuidora Alimentos Sur', '88.555.666-7', 'compras@alisur.cl'),
            ('Estudio Jurídico Silva', '76.888.999-0', 'contacto@silvalaw.cl'),
            ('StartUp Innova SpA', '77.777.888-9', 'cto@innova.cl')
        ]
        
        clientes_objs = []
        for nombre, rut, mail in clientes_fake:
            cli, _ = Cliente.objects.get_or_create(
                rut=rut,
                empresa=empresa,
                defaults={
                    'nombre': nombre,
                    'email': mail,
                    'direccion': 'Dirección comercial #123',
                    'telefono': '+56999999999'
                }
            )
            clientes_objs.append(cli)

        # Generar Cotizaciones
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)
        
        total_cots = 0
        
        # Iterar por días para distribuir cotizaciones
        current_date = start_date
        while current_date <= end_date:
            # Probabilidad de cotización por día (30%)
            if random.random() < 0.4:
                cliente = random.choice(clientes_objs)
                vendedor = random.choice(vendedores)
                
                # Crear cotización
                cot = Cotizacion(
                    cliente=cliente,
                    empresa=empresa,
                    usuario_creador=vendedor,
                    canal_preferencia=random.choice([Cotizacion.Canal.EMAIL, Cotizacion.Canal.WHATSAPP]),
                    notas='Cotización generada automáticamente por demo.'
                )
                cot.save() # Para tener ID
                
                # Hackear la fecha de creación (auto_now_add no deja setearla en init)
                cot.fecha_creacion = current_date
                # Fecha vencimiento = +30 días
                cot.fecha_vencimiento = (current_date + timedelta(days=30)).date()
                
                # Estado aleatorio basado en antigüedad
                days_old = (end_date - current_date).days
                
                if days_old > 60: # Muy antiguas
                    estado = random.choice([Cotizacion.Estado.ACEPTADA, Cotizacion.Estado.RECHAZADA, Cotizacion.Estado.ENVIADA])
                elif days_old > 30: # Antiguas
                    estado = random.choice([Cotizacion.Estado.ENVIADA, Cotizacion.Estado.ACEPTADA, Cotizacion.Estado.RECHAZADA])
                elif days_old > 7: # Recientes
                    estado = random.choice([Cotizacion.Estado.ENVIADA, Cotizacion.Estado.ENVIADA, Cotizacion.Estado.BORRADOR])
                else: # Nuevas (última semana)
                    estado = random.choice([Cotizacion.Estado.BORRADOR, Cotizacion.Estado.ENVIADA])
                
                cot.estado = estado
                
                # Si está decidida (Aceptada/Rechazada), poner datos de decisión
                if estado in [Cotizacion.Estado.ACEPTADA, Cotizacion.Estado.RECHAZADA]:
                    cot.usuario_decision = admin # Usar el admin como decisor
                    cot.fecha_decision = current_date + timedelta(days=random.randint(1, 10))
                
                cot.save()
                
                # Agregar items (1 a 5 items)
                num_items = random.randint(1, 5)
                prods_sample = random.sample(productos, num_items)
                
                for p in prods_sample:
                    cantidad = random.randint(1, 10)
                    DetalleCotizacion.objects.create(
                        cotizacion=cot,
                        producto=p,
                        cantidad=cantidad,
                        precio_unitario=p.precio,
                        impuesto=p.impuesto_total
                    )
                
                cot.calcular_totales()
                total_cots += 1
            
            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Generación completada existosamente.'))
        self.stdout.write(self.style.SUCCESS(f'Total Cotizaciones: {total_cots}'))
        self.stdout.write(self.style.SUCCESS(f'Empresa: {empresa.nombre}'))
        self.stdout.write(self.style.SUCCESS(f'Usuarios ventas: {[u.email for u in vendedores]} (Pass: vendedor123)'))
        self.stdout.write(self.style.SUCCESS(f'Usuario admin: {admin.email} (Pass: admin123)'))
