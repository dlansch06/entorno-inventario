import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import format_html # Para poner colores
from django.utils import timezone
from .models import Perfil, Equipo, Designacion, Estudiante, Nota, Asistencia, Comunicado, Actividad

# --- ACCIÓN: EXPORTAR A EXCEL PRO ---
@admin.action(description='Descargar Reporte Excel (Oficial)')
def exportar_excel_pro(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario"

    # Estilos
    header_font = Font(name='Arial', bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4B2C20", end_color="4B2C20", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                    top=Side(style='thin'), bottom=Side(style='thin'))

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo.jpg') # Asegura esta ruta
    if os.path.exists(logo_path):
        img = XLImage(logo_path)
        img.width, img.height = 80, 80
        ws.add_image(img, 'A1') 

    # Título
    ws.merge_cells('B2:F2')
    ws['B2'] = "I.E. JUANA CERVANTES - REPORTE DE INVENTARIO"
    ws['B2'].font = Font(size=14, bold=True)
    ws['B2'].alignment = center_align

    # Encabezados
    headers = ['SERIE', 'CATEGORÍA', 'MARCA', 'MODELO', 'ESTADO', 'INGRESO COLEGIO']
    for col_num, column_title in enumerate(headers, 1):
        cell = ws.cell(row=6, column=col_num, value=column_title)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = border

    # Datos
    for row_num, obj in enumerate(queryset, 7):
        data = [
            obj.serie, obj.get_categoria_display(), obj.marca, obj.modelo,
            obj.estado, obj.fecha_ingreso_colegio.strftime('%d/%m/%Y') if obj.fecha_ingreso_colegio else ""
        ]
        for col_num, cell_value in enumerate(data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=cell_value)
            cell.border = border

    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 20

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.xlsx"'
    wb.save(response)
    return response

# --- CONFIGURACIÓN ADMIN: EQUIPOS ---
@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('serie', 'marca', 'modelo', 'color_estado', 'aula_actual', 'fecha_ingreso_colegio')
    list_filter = ('estado', 'categoria', 'fecha_ingreso_colegio')
    search_fields = ('serie', 'marca', 'modelo')
    actions = [exportar_excel_pro]

    def color_estado(self, obj):
        colores = {
            'DISPONIBLE': 'green',
            'EN_USO': 'blue',
            'MANTENIMIENTO': 'orange',
            'BAJA': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colores.get(obj.estado, 'black'),
            obj.get_estado_display()
        )
    color_estado.short_description = 'Estado Actual'

# --- CONFIGURACIÓN ADMIN: PERFILES (APROBACIÓN) ---
@admin.action(description='Aprobar usuarios seleccionados')
def aprobar_usuarios(modeladmin, request, queryset):
    queryset.update(esta_aprobado=True, fecha_aprobacion=timezone.now())

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'esta_aprobado', 'grado_asignado', 'seccion_asignada')
    list_filter = ('rol', 'esta_aprobado', 'grado_asignado')
    list_editable = ('esta_aprobado',)
    actions = [aprobar_usuarios]

# --- CONFIGURACIÓN ADMIN: ESTUDIANTES ---
@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('apellidos', 'nombres', 'dni', 'nivel', 'grado', 'seccion', 'padre')
    list_filter = ('nivel', 'grado', 'seccion')
    search_fields = ('dni', 'apellidos')

# --- CONFIGURACIÓN ADMIN: DESIGNACIONES ---
@admin.register(Designacion)
class DesignacionAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'persona_responsable', 'fecha_entrega', 'fecha_devolucion_real')
    list_filter = ('fecha_entrega', 'fecha_devolucion_real')

# Registrar los restantes para gestión rápida
admin.site.register(Nota)
admin.site.register(Asistencia)
admin.site.register(Comunicado)
admin.site.register(Actividad)