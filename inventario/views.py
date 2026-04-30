import io
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponse
from .models import Equipo
from django.contrib import messages
# Librerías para PDF y Excel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage # Para el logo
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side # Para el diseño
from datetime import datetime
# --- 1. AUTENTICACIÓN Y ACCESO ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/admin/') if request.user.is_staff else redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_staff:
                return redirect('/admin/')
            return redirect('dashboard')
        else:
            # Esto avisa si los datos están mal
            messages.error(request, "Usuario o contraseña incorrectos.")
            
    return render(request, 'login.html')

def invitado_view(request):
    """Crea una sesión temporal para invitados sin necesidad de contraseña."""
    request.session['es_invitado'] = True
    return redirect('dashboard')

def logout_view(request):
    """Limpia TODO: Sesión de Admin y Sesión de Invitado."""
    auth_logout(request)
    request.session.flush() 
    return redirect('login')


# --- 2. DASHBOARD (PANEL DE CONTROL) ---

def dashboard_view(request):
    """Muestra el resumen estadístico con las tarjetas de colores."""
    if not request.user.is_authenticated and not request.session.get('es_invitado'):
        return redirect('login')
    
    context = {
        'total': Equipo.objects.count(),
        'disponible': Equipo.objects.filter(estado='DISPONIBLE').count(),
        'en_uso': Equipo.objects.filter(estado='EN_USO').count(),
        'mantenimiento': Equipo.objects.filter(estado='MANTENIMIENTO').count(),
        'no_existe': Equipo.objects.filter(estado='NO_EXISTE').count(),
        'equipos_recientes': Equipo.objects.all().order_by('-id')[:5],
    }
    return render(request, 'dashboard.html', context)


# --- 3. EQUIPOS Y REPORTES ---
def inventario_view(request):
    """Muestra la tabla de equipos con filtros de búsqueda."""
    if not request.user.is_authenticated and not request.session.get('es_invitado'):
        return redirect('login')

    equipos = Equipo.objects.all()
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    if q:
        equipos = equipos.filter(
            Q(serie__icontains=q) |
            Q(marca__icontains=q) |
            Q(modelo__icontains=q)
        )
    if estado:
        equipos = equipos.filter(estado=estado)

    return render(request, 'inventario.html', {
        'equipos': equipos, 
        'q': q, 
        'estado_actual': estado
    })

def reportes_view(request):
    """Maneja la tabla, los filtros de búsqueda y las exportaciones."""
    if not request.user.is_authenticated and not request.session.get('es_invitado'):
        return redirect('login')

    equipos = Equipo.objects.all()
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    if q:
        equipos = equipos.filter(
            Q(serie__icontains=q) |
            Q(marca__icontains=q) |
            Q(modelo__icontains=q)
        )
    if estado:
        equipos = equipos.filter(estado=estado)

    # Lógica de exportación
    export_type = request.GET.get('export')
    if export_type == 'excel':
        return exportar_excel(equipos)
    elif export_type == 'pdf':
        return exportar_pdf(equipos)

    return render(request, 'reportes.html', {
        'equipos': equipos, 
        'q': q, 
        'estado_actual': estado
    })

def acerca_de_view(request):
    if not request.user.is_authenticated and not request.session.get('es_invitado'):
        return redirect('login')
    
    
    return render(request, 'info.html')
    
    
    return render(request, 'info.html')
def exportar_excel(queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario Juana Cervantes"

    # --- DISEÑO DE ESTILOS ---
    header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    border_style = Border(left=Side(style='thin'), right=Side(style='thin'), 
                         top=Side(style='thin'), bottom=Side(style='thin'))
    center_align = Alignment(horizontal="center", vertical="center")

    # --- ENCABEZADO PERSONALIZADO (Logo y Título) ---
    # Dejamos las primeras filas para el logo y título
    ws.merge_cells('B2:F2')
    ws['B2'] = "I.E. JUANA CERVANTES DE BOLOGNESI"
    ws['B2'].font = Font(bold=True, size=16, color="003366")
    ws['B2'].alignment = center_align

    ws.merge_cells('B3:F3')
    ws['B3'] = f"REPORTE GENERAL DE INVENTARIO - Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws['B3'].font = Font(italic=True, size=10)
    ws['B3'].alignment = center_align

    # Cargar Logo (Asegúrate de que la ruta sea correcta en tu proyecto)
    try:
        img = ExcelImage('static/inventario/logo.jpg') 
        img.width = 60 # Ajustar tamaño
        img.height = 60
        ws.add_image(img, 'A1')
    except:
        pass # Si no encuentra la imagen, el reporte se genera igual

    # --- TABLA DE DATOS ---
    headers = ['SERIE', 'MARCA', 'MODELO', 'ESTADO', 'UBICACIÓN', 'RESPONSABLE']
    start_row = 5 # La tabla empieza en la fila 5
    
    # Escribir encabezados de tabla
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = border_style

    # Escribir datos del queryset
    for row_num, e in enumerate(queryset, start_row + 1):
        row_data = [
            e.serie, 
            e.marca if hasattr(e, 'marca') else "---", 
            e.modelo, 
            e.estado, 
            e.aula, 
            e.responsable if hasattr(e, 'responsable') else "No asignado"
        ]
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            cell.border = border_style
            cell.alignment = Alignment(vertical="center", horizontal="left")

    # --- AJUSTE AUTOMÁTICO DE COLUMNAS ---
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length: max_length = len(str(cell.value))
            except: pass
        ws.column_dimensions[column].width = max_length + 4

    # --- RESPUESTA HTTP ---
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Reporte_Inventario_JC.xlsx'
    wb.save(response)
    return response          
    

def exportar_pdf(queryset):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    p.setFillColor(colors.HexColor("#003366"))
    p.rect(0, h-80, w, 80, fill=True, stroke=False)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, h-45, "REPORTE DE INVENTARIO - I.E. JUANA CERVANTES")
    
    # Tabla de datos (columnas ajustadas para 4 campos)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    y = h - 120
    
    # Ajustamos posiciones X para que se vea bien distribuido
    p.drawString(50, y, "Serie")
    p.drawString(180, y, "Modelo")
    p.drawString(380, y, "Estado")
    p.drawString(480, y, "Aula")
    p.line(50, y-5, 550, y-5)

    p.setFont("Helvetica", 9)
    y -= 25
    for e in queryset:
        p.drawString(50, y, str(e.serie))
        p.drawString(180, y, str(e.modelo)[:35])
        p.drawString(380, y, str(e.estado))
        p.drawString(480, y, str(e.aula))
        y -= 20
        
        if y < 50: 
            p.showPage()
            y = h - 50

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')