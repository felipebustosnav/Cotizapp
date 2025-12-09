"""
Generador de PDFs para cotizaciones usando ReportLab.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime


def generar_pdf_cotizacion(cotizacion):
    """
    Genera un PDF para una cotización.
    
    Args:
        cotizacion: Instancia del modelo Cotizacion
    
    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph(f"COTIZACIÓN N° {cotizacion.numero}", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de la empresa
    empresa_data = [
        ['EMPRESA:', cotizacion.empresa.nombre],
        ['RUT:', cotizacion.empresa.rut],
        ['Dirección:', cotizacion.empresa.direccion or 'N/A'],
        ['Teléfono:', cotizacion.empresa.telefono or 'N/A'],
        ['Email:', cotizacion.empresa.email or 'N/A'],
    ]
    
    empresa_table = Table(empresa_data, colWidths=[1.5*inch, 4*inch])
    empresa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(empresa_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del cliente
    cliente_data = [
        ['CLIENTE:', cotizacion.cliente.nombre],
        ['RUT:', cotizacion.cliente.formatear_rut()],
        ['Email:', cotizacion.cliente.email],
        ['Teléfono:', cotizacion.cliente.telefono or 'N/A'],
    ]
    
    cliente_table = Table(cliente_data, colWidths=[1.5*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de fechas
    fecha_data = [
        ['Fecha de Emisión:', cotizacion.fecha_creacion.strftime('%d/%m/%Y')],
        ['Fecha de Vencimiento:', cotizacion.fecha_vencimiento.strftime('%d/%m/%Y')],
        ['Estado:', cotizacion.get_estado_display()],
    ]
    
    fecha_table = Table(fecha_data, colWidths=[1.5*inch, 4*inch])
    fecha_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(fecha_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Tabla de productos
    productos_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Impuesto', 'Subtotal']]
    
    for detalle in cotizacion.detalles.all():
        productos_data.append([
            detalle.producto.nombre,
            str(detalle.cantidad),
            f'${detalle.precio_unitario:,.0f}',
            f'{detalle.impuesto}%',
            f'${detalle.subtotal:,.0f}'
        ])
    
    productos_table = Table(productos_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
    productos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    elements.append(productos_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totales
    totales_data = [
        ['SUBTOTAL:', f'${cotizacion.subtotal:,.0f}'],
        ['TOTAL:', f'${cotizacion.total:,.0f}'],
    ]
    
    totales_table = Table(totales_data, colWidths=[4.5*inch, 2*inch])
    totales_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('BACKGROUND', (1, -1), (1, -1), colors.HexColor('#e8f0fe')),
    ]))
    
    elements.append(totales_table)
    
    # Notas
    if cotizacion.notas:
        elements.append(Spacer(1, 0.4*inch))
        elements.append(Paragraph('<b>Notas:</b>', styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(cotizacion.notas, styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
