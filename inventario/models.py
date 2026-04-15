from django.db import models
from django.contrib.auth.models import User

# --- PANORAMA 1: USUARIOS, ROLES Y SEGURIDAD ---
# Nota: La contraseña ya está incluida en el modelo 'User' de Django.
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


# --- PANORAMA 2 Y 3: EQUIPOS Y ESTADOS DE STOCK ---
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
    registrado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        editable=False # Esto evita que alguien lo cambie manualmente
    )
    fecha_registro_sistema = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.serie


# --- PANORAMA 2: DESIGNACIÓN, PRESTAMOS Y DEVOLUCIONES ---
class Designacion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    docente_recibe = models.CharField(max_length=150, verbose_name="Docente responsable")
    
    # Fechas solicitadas
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    fecha_devolucion_prevista = models.DateTimeField(verbose_name="Fecha prevista de devolución")
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True, verbose_name="Fecha real de retorno")
    
    # Registro de quién hizo la operación (El Profesor Encargado)
    encargado_registro = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Designación"
        verbose_name_plural = "Designaciones"

    def __str__(self):
        return f"Equipo {self.equipo.serie} asignado a {self.docente_recibe}"
    