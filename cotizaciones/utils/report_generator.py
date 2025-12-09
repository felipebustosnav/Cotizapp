from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.http import HttpResponse
from django.utils import timezone
import io

def generar_reporte_pdf(empresa, stats):
    """
    Genera un PDF con el reporte ejecutivo de la empresa.
    stats es un diccionario con: resumen, ventas_mensuales, top_productos
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    # Estilos Personalizados
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'), # Dark Blue
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    style_subtitle = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceBefore=15,
        spaceAfter=10
    )

    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )
    
    elements = []

    # 1. Encabezado (Logo y Título)
    if empresa.logo:
        try:
            img = Image(empresa.logo.path)
            # Escalar imagen manteniendo ratio
            max_width = 1.5 * inch
            max_height = 0.8 * inch
            cw = img.drawWidth
            ch = img.drawHeight
            ratio = min(max_width/cw, max_height/ch)
            img.drawWidth = cw * ratio
            img.drawHeight = ch * ratio
            elements.append(img)
            elements.append(Spacer(1, 10))
        except Exception:
            pass # Si falla logo, seguimos

    elements.append(Paragraph(f"Reporte Ejecutivo de Ventas", style_title))
    elements.append(Paragraph(f"Empresa: {empresa.nombre}", style_title))
    elements.append(Paragraph(f"Fecha de Emisión: {timezone.now().strftime('%d/%m/%Y %H:%M')}", style_normal))
    elements.append(Spacer(1, 20))

    # 2. Resumen General
    elements.append(Paragraph("Resumen General", style_subtitle))
    
    resumen_data = [
        ['Indicador', 'Valor'],
        ['Total Cotizaciones Generadas', str(stats['resumen']['total_cotizaciones'])],
        ['Tasa de Aprobación', f"{stats['resumen']['tasa_aprobacion']}%"],
        ['Monto Total Aprobado', f"${stats['resumen']['monto_total_aprobado']:,.0f}".replace(',', '.')] # Formato chileno simple
    ]
    
    t_resumen = Table(resumen_data, colWidths=[300, 150])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
    ]))
    elements.append(t_resumen)
    elements.append(Spacer(1, 20))

    # 3. Ventas Mensuales (Tabla)
    elements.append(Paragraph("Ventas Mensuales (Últimos 6 meses)", style_subtitle))
    
    if stats['ventas_mensuales']:
        ventas_data = [['Mes', 'Cantidad', 'Total Vendido']]
        for venta in stats['ventas_mensuales']:
            ventas_data.append([
                venta['mes'],
                str(venta['cantidad']),
                f"${venta['total']:,.0f}".replace(',', '.')
            ])
        
        t_ventas = Table(ventas_data, colWidths=[200, 100, 150])
        t_ventas.setStyle(TableStyle([
             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
             ('GRID', (0, 0), (-1, -1), 1, colors.black),
             ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
             ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ]))
        elements.append(t_ventas)
    else:
        elements.append(Paragraph("No hay registros de ventas aprobadas en el periodo.", style_normal))

    elements.append(Spacer(1, 20))

    # 4. Top Productos
    elements.append(Paragraph("Productos Más Cotizados", style_subtitle))
    
    if stats['top_productos']:
        prod_data = [['Producto', 'Unidades Cotizadas']]
        for p in stats['top_productos']:
            prod_data.append([p['nombre'][:50], str(p['cantidad'])]) # Truncar nombre largo
            
        t_prod = Table(prod_data, colWidths=[350, 100])
        t_prod.setStyle(TableStyle([
             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
             ('GRID', (0, 0), (-1, -1), 1, colors.black),
             ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        elements.append(t_prod)
    else:
        elements.append(Paragraph("No hay información de productos.", style_normal))

    elements.append(Spacer(1, 20))

    # 5. Análisis de Mensajería Automática
    if 'automatizacion' in stats:
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceBefore=10, spaceAfter=20))
        elements.append(Paragraph("Análisis de Mensajería Automática", style_title))
        
        auto = stats['automatizacion']
        
        # Tabla de KPIs Extendida
        kpi_data = [
            ['Volumen', 'Aceptadas', 'Rechazadas', 'Efectividad', 'Prom. Descuento'],
            [
                str(auto['total_ofertas']),
                str(auto['ofertas_aceptadas']),
                str(auto['ofertas_rechazadas']),
                f"{auto['tasa_conversion']}%",
                f"${auto['promedio_descuento']:,.0f}".replace(',', '.')
            ]
        ]
        
        t_kpi = Table(kpi_data, colWidths=[100, 80, 80, 80, 100])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0f2fe')), # Light blue header
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0369a1')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 15))

        # --- Análisis de Eficiencia por Descuento ---
        if auto['eficiencia_por_descuento']:
            elements.append(Paragraph("Efectividad por Estrategia de Descuento:", style_subtitle))
            
            # Encontrar el mejor porcentaje
            mejor_pct = max(auto['eficiencia_por_descuento'], key=lambda x: x['tasa'])
            if mejor_pct['tasa'] > 0:
                texto_insight = f"<b>INSIGHT:</b> La estrategia más convincente ha sido ofrecer un descuento del <b>{mejor_pct['porcentaje']}</b>, logrando una tasa de aceptación del <b>{mejor_pct['tasa']}%</b>."
                elements.append(Paragraph(texto_insight, style_normal))
                elements.append(Spacer(1, 10))
            
            eff_data = [['% Descuento', 'Enviadas', 'Aceptadas', 'Tasa Éxito']]
            for item in auto['eficiencia_por_descuento']:
                eff_data.append([
                    item['porcentaje'],
                    str(item['enviadas']),
                    str(item['aceptadas']),
                    f"{item['tasa']}%"
                ])
                
            t_eff = Table(eff_data, colWidths=[100, 100, 100, 100])
            t_eff.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0fdf4')), # Light green header
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ]))
            elements.append(t_eff)
            elements.append(Spacer(1, 15))

        # Detalle de Estados (Resumido)
        if auto['estado_ofertas']:
            elements.append(Paragraph("Distribución de Estados:", style_subtitle))
            estado_data = [['Estado', 'Cantidad']]
            for estado in auto['estado_ofertas']:
                estado_data.append([estado['nombre'], str(estado['cantidad'])])
            
            t_estados = Table(estado_data, colWidths=[200, 100])
            t_estados.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ]))
            elements.append(t_estados)
        else:
            elements.append(Paragraph("No se han generado ofertas automáticas aún.", style_normal))

    else:
        pass # No data structure available

    # Footer
    elements.append(Spacer(1, 40))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Paragraph("Documento generado automáticamente por sistema de gestión CotizApp.", style_normal))

    # Definir función de fondo
    def add_background(canvas, doc):
        canvas.saveState()
        # Naranjo CotizApp con baja opacidad
        canvas.setFillColor(colors.HexColor('#F97316'))
        canvas.setFillAlpha(0.05) # Muy sutil (5%)
        
        # Diseño geométrico: Círculo grande abajo a la derecha
        width, height = doc.pagesize
        canvas.circle(width, 0, 400, stroke=0, fill=1)
        
        # Diseño geométrico: Círculo pequeño arriba a la izquierda
        canvas.circle(0, height, 200, stroke=0, fill=1)
        
        # Restaurar estado
        canvas.restoreState()

    # Build con fondo
    doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)
    
    # Response
    pdf = buffer.getvalue()
    
    # Cerrar y retornar
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"Reporte_Ejecutivo_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
