import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib import admin
from .models import Perfil, Equipo, Designacion

@admin.action(description='Exportar a Excel con Logo y Diseño')
def exportar_excel_pro(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte Oficial"

    
    header_font = Font(name='Arial', bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4B2C20", end_color="4B2C20", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                    top=Side(style='thin'), bottom=Side(style='thin'))

    
    logo_path = os.path.join(settings.BASE_DIR, 'inventario/static/inventario/logo.jpg')
    if os.path.exists(logo_path):
        img = XLImage(logo_path)
        img.width = 80  
        img.height = 80
        ws.add_image(img, 'A1') 

    ws.merge_cells('B2:E2')
    titulo = ws['B2']
    titulo.value = "SISTEMA DE INVENTARIO - REPORTE OFICIAL"
    titulo.font = Font(size=16, bold=True, color="4B2C20")
    titulo.alignment = center_align

    headers = ['SERIE', 'MARCA', 'MODELO', 'ESTADO', 'FECHA INGRESO']
    row_num = 6
    for col_num, column_title in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = border

    for obj in queryset:
        row_num += 1
        data = [
            obj.serie,
            obj.marca,
            obj.modelo,
            obj.estado,
            obj.fecha_ingreso_colegio.strftime('%d/%m/%Y') if obj.fecha_ingreso_colegio else ""
        ]
        for col_num, cell_value in enumerate(data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.border = border
            cell.alignment = Alignment(horizontal="left")

    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 20

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_institucional.xlsx"'
    wb.save(response)
    return response
@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('serie', 'marca', 'modelo', 'estado', 'get_auditoria')
    list_filter = ('estado', 'marca', 'fecha_registro_sistema')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Si es un registro nuevo
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)

    def get_auditoria(self, obj):
        if obj.registrado_por:
            return f"{obj.registrado_por.username} - {obj.fecha_registro_sistema.strftime('%d/%m/%Y %H:%M')}"
        return "No registrado"
    
    get_auditoria.short_description = 'Registro (Usuario - Fecha/Hora)'

    def get_list_display(self, request):

        if request.user.is_superuser:
            return ('serie', 'marca', 'modelo', 'estado', 'get_auditoria')
        # Si es profesor, solo ve los datos básicos
        return ('serie', 'marca', 'modelo', 'estado')