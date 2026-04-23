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
    # Seguridad: Si no es admin ni invitado, fuera.
    if not request.user.is_authenticated and not request.session.get('es_invitado'):
        return redirect('login')
    
    context = {
        'total': Equipo.objects.count(),
        'disponible': Equipo.objects.filter(estado='DISPONIBLE').count(),
        'en_uso': Equipo.objects.filter(estado='EN_USO').count(),
        'mantenimiento': Equipo.objects.filter(estado='MANTENIMIENTO').count(),
        'no_existe': Equipo.objects.filter(estado='NO_EXISTE').count(),
    }
    return render(request, 'dashboard.html', context)


# --- 3. EQUIPOS Y REPORTES ---

def reportes_view(request):
    """Maneja la tabla, los filtros de búsqueda y las exportaciones."""
    if not request.user.is_authenticated and not request.session.get('es_invitado'):
        return redirect('login')

    equipos = Equipo.objects.all()
    
    # Captura de filtros
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    if q:
        equipos = equipos.filter(
            Q(serie__icontains=q) |
            Q(modelo__icontains=q)
        )
    if estado:
        equipos = equipos.filter(estado=estado)

    # Lógica de exportación
    if 'export' in request.GET:
        tipo = request.GET.get('export')
        if tipo == 'excel': 
            return exportar_excel(equipos)
        if tipo == 'pdf': 
            return exportar_pdf(equipos)

    return render(request, 'reportes.html', {
        'equipos': equipos, 
        'q': q, 
        'estado': estado
    })


def exportar_excel(queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"
    
    # Encabezados actualizados
    ws.append(['Serie', 'Modelo', 'Estado', 'Aula'])
    
    for e in queryset:
        # Solo usamos los campos que sí tienes en tu modelo
        ws.append([
            e.serie, 
            e.modelo, 
            e.estado, 
            e.aula,
            e.responsable 
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=inventario_jc.xlsx'
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