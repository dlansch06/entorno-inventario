from django.db import models
from django.contrib.auth.models import User

# --- 1. USUARIOS Y ROLES ---
class Perfil(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador General'),
        ('ENCAR', 'Profesor Encargado de Inventario'),
        ('SECRET', 'Secretario / Consulta'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=10, choices=ROLES, default='SECRET')
    dni = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"


# --- 2. EQUIPOS (Con los campos de entrega incluidos) ---
class Equipo(models.Model):
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_USO', 'En Uso'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
        ('NO_EXISTE', 'No Existe / Dado de Baja'),
    ]

    serie = models.CharField(max_length=100, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='DISPONIBLE')
    fecha_ingreso_colegio = models.DateField(verbose_name="Fecha de ingreso al colegio")
    observaciones = models.TextField(blank=True, null=True)
    
    # --- NUEVOS CAMPOS DE ASIGNACIÓN DIRECTA ---
    responsable = models.CharField(max_length=150, verbose_name="Entregado a", blank=True, null=True)
    aula = models.CharField(max_length=100, verbose_name="Aula", blank=True, null=True)
    fecha_entrega = models.DateField(verbose_name="Fecha de Entrega", blank=True, null=True)
    fecha_devolucion = models.DateField(verbose_name="Fecha de Devolución Prevista", blank=True, null=True)

    # Auditoría
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False)
    fecha_registro_sistema = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.serie} ({self.modelo})"


# --- 3. HISTORIAL DE DESIGNACIONES (Opcional, para registro histórico) ---
class Designacion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    docente_recibe = models.CharField(max_length=150, verbose_name="Docente responsable")
    aula_destino = models.CharField(max_length=100, verbose_name="Aula", null=True)
    
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    fecha_devolucion_prevista = models.DateTimeField(verbose_name="Fecha prevista de devolución")
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True, verbose_name="Fecha real de retorno")
    
    encargado_registro = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Designación"
        verbose_name_plural = "Designaciones"

    def __str__(self):
        return f"Equipo {self.equipo.serie} asignado a {self.docente_recibe}"