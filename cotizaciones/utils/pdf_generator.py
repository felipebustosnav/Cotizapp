"""
Generador de PDFs para cotizaciones usando ReportLab con diseño profesional.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings

def generar_pdf_cotizacion(cotizacion):
    """
    Genera un PDF para una cotización con diseño profesional.
    """
    buffer = BytesIO()
    # Margenes ajustados para look limpio
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # --- Colores de marca ---
    primary_color = colors.HexColor('#F97316') # Orange from the app info
    secondary_color = colors.HexColor('#333333')
    light_bg = colors.HexColor('#F3F4F6')
    
    # --- HEADER ---
    # Logo a la izquierda, Info empresa a la derecha
    
    # Preparar logo EMPRESA
    from reportlab.lib.utils import ImageReader
    
    logo_img = []
    if cotizacion.empresa.logo:
        try:
            logo_path = cotizacion.empresa.logo.path
            
            # Usar ImageReader para obtener dimensiones sin abrir con PIL explícitamente y sin dependencias extra
            # a veces ya instala pillow reportlab
            img_reader = ImageReader(logo_path)
            iw, ih = img_reader.getSize()
            aspect = ih / float(iw)
            
            # Definir caja maxima
            max_width = 1.5 * inch
            max_height = 1.0 * inch
            
            # Calcular dimensiones ajustadas
            width = max_width
            height = width * aspect
            
            if height > max_height:
                height = max_height
                width = height / aspect
                
            img = Image(logo_path, width=width, height=height) 
            img.hAlign = 'LEFT'
            logo_img = [img]
        except Exception as e:
            # print(f"Error cargando logo: {e}") 
            logo_img = [] # Fallback

    # Info Empresa Texto (Sin duplicados)
    empresa_style = ParagraphStyle('EmpresaInfo', parent=styles['Normal'], fontSize=9, leading=12, alignment=TA_RIGHT, textColor=secondary_color)
    empresa_info = [
        Paragraph(f"<b>{cotizacion.empresa.nombre}</b>", empresa_style),
        Paragraph(cotizacion.empresa.rut or '', empresa_style),
        Paragraph(cotizacion.empresa.direccion or '', empresa_style),
        Paragraph(cotizacion.empresa.telefono or '', empresa_style),
        Paragraph(cotizacion.empresa.email or '', empresa_style),
    ]
    
    # Tabla Cabecera (Logo vs Info)
    header_data = [[logo_img if logo_img else "", empresa_info]]
    header_table = Table(header_data, colWidths=[3.5*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # --- TÍTULO Y DATOS CLIENTE ---
    
    # Título Grande
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, textColor=primary_color, spaceAfter=2)
    elements.append(Paragraph("COTIZACIÓN", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Layout: Bloque Cliente (Izquierda) | Bloque Detalles Cotización (Derecha)
    
    # Estilos
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=8, textColor=colors.gray)
    value_style = ParagraphStyle('Value', parent=styles['Normal'], fontSize=10, textColor=secondary_color, leading=12)
    
    cliente_bloque = [
        Paragraph("PREPARADO PARA:", label_style),
        Spacer(1, 2),
        Paragraph(f"<b>{cotizacion.cliente.nombre}</b>", value_style),
        Paragraph(f"RUT: {cotizacion.cliente.formatear_rut()}", value_style),
        Paragraph(cotizacion.cliente.email or '', value_style),
        Paragraph(cotizacion.cliente.telefono or '', value_style),
    ]
    
    datos_bloque = [
        # Número
        [Paragraph("NÚMERO:", label_style), Paragraph(f"<b>{cotizacion.numero}</b>", value_style)],
        # Fecha
        [Paragraph("FECHA:", label_style), Paragraph(cotizacion.fecha_creacion.strftime('%d/%m/%Y'), value_style)],
        # Vencimiento
        [Paragraph("VÁLIDO HASTA:", label_style), Paragraph(cotizacion.fecha_vencimiento.strftime('%d/%m/%Y'), value_style)],
        # Estado
        [Paragraph("ESTADO:", label_style), Paragraph(cotizacion.get_estado_display().upper(), value_style)],
    ]
    
    # Tabla interna para datos a la derecha
    datos_table = Table(datos_bloque, colWidths=[1*inch, 1.5*inch])
    datos_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    info_layout_data = [[cliente_bloque, datos_table]]
    info_table = Table(info_layout_data, colWidths=[4*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # --- TABLA DE ITEMS ---
    
    headers = ['DESCRIPCIÓN', 'CANT.', 'PRECIO', 'IMP.', 'TOTAL']
    table_data = [headers]
    
    for detalle in cotizacion.detalles.all():
        row = [
            Paragraph(detalle.producto.nombre, value_style),
            str(detalle.cantidad),
            f"${detalle.precio_unitario:,.0f}",
            f"{detalle.impuesto:g}%",
            f"${detalle.subtotal:,.0f}"
        ]
        table_data.append(row)
        
    # Estilo de Tabla Profesional
    # Anchos
    col_widths = [3.5*inch, 0.8*inch, 1.2*inch, 0.8*inch, 1.2*inch]
    
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), secondary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'), # Descripcion Left
        ('ALIGN', (1, 0), (-1, 0), 'RIGHT'), # Numeros Right
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]), # Alternating colors
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- TOTALES ---
    
    neto_total = 0
    impuesto_total = 0
    for d in cotizacion.detalles.all():
        base = d.precio_unitario * d.cantidad
        imp = base * (d.impuesto / 100)
        neto_total += base
        impuesto_total += imp
        
    gran_total = cotizacion.total 
    
    totales_block = [
        ['Subtotal Neto:', f"${neto_total:,.0f}"],
        ['Impuestos:', f"${impuesto_total:,.0f}"],
        ['TOTAL:', f"${gran_total:,.0f}"]
    ]
    
    totales_table = Table(totales_block, colWidths=[1.5*inch, 1.2*inch])
    totales_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'), 
        ('FONTNAME', (1, 0), (1, -2), 'Helvetica'), 
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), 
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('TEXTCOLOR', (0, -1), (-1, -1), primary_color), 
        ('LINEABOVE', (0, -1), (-1, -1), 1, secondary_color),
        ('TOPPADDING', (0, -1), (-1, -1), 6),
    ]))
    
    layout_totales = Table([[ "", totales_table ]], colWidths=[4.8*inch, 2.7*inch])
    layout_totales.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(layout_totales)
    
    # --- FOOTER / NOTAS ---
    if cotizacion.notas:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("NOTAS ADICIONALES", label_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(cotizacion.notas, ParagraphStyle('Notes', parent=styles['Normal'], fontSize=9, textColor=colors.gray, backColor=light_bg, borderPadding=10, borderRadius=5)))

    # Mensaje final
    elements.append(Spacer(1, 0.5*inch))
    center_style = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.gray)
    elements.append(Paragraph("Gracias por su preferencia", center_style))
    
    # --- POWERED BY COTIZAPP ---
    elements.append(Spacer(1, 0.3*inch))
    
    # --- POWERED BY COTIZAPP ---
    elements.append(Spacer(1, 0.3*inch))
    
    # Estilo "Logo" texto (mismo estilo que título pero ajustado)
    logo_text_style = ParagraphStyle(
        'CotizAppLogo',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceBefore=0,
        spaceAfter=0
    )
    
    powered_style = ParagraphStyle(
        'Powered',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.gray
    )
    
    # Tabla para centrar "Powered by" y "CotizApp"
    footer_data = [
        [Paragraph("Powered by", powered_style)],
        [Paragraph("CotizApp", logo_text_style)]
    ]
    
    footer_table = Table(footer_data, colWidths=[7.5*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEADING', (0, 0), (-1, -1), 8), # Reducir espacio entre lineas
    ]))
    elements.append(footer_table)
    
    doc.build(elements)
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
