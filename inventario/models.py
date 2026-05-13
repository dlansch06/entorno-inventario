from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Perfil(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador General'),
        ('DIRECTOR', 'Director del Colegio'),
        ('ENCAR', 'Profesor Encargado de Inventario'),
        ('DOCENTE', 'Docente Tutor'),
        ('SECRETARIA', 'Secretaria'),
        ('PADRE', 'Padre de Familia'),
    ]
    NIVELES = [('PRI', 'Primaria'), ('SEC', 'Secundaria')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='PADRE')
    esta_aprobado = models.BooleanField(default=False) 
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    nivel_asignado = models.CharField(max_length=3, choices=NIVELES, blank=True, null=True)
    grado_asignado = models.CharField(max_length=10, blank=True, null=True)
    seccion_asignada = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        estado = "Aprobado" if self.esta_aprobado else "Pendiente"
        return f"{self.user.username} ({self.get_rol_display()}) - {estado}"

class EquipoManager(models.Manager):
    def activos(self):
        return self.filter(eliminado=False)

class Equipo(models.Model):
    CATEGORIAS = [
        ('LAPTOP', 'Laptop / Computadora'),
        ('SONIDO', 'Equipo de Sonido / Parlantes'),
        ('ELECTRO', 'Electrodoméstico'),
        ('ACCESORIO', 'Accesorio'),
    ]
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_USO', 'En Uso'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
        ('BAJA', 'Baja'),
    ]

    serie = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='LAPTOP')
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    fecha_ingreso_colegio = models.DateField(verbose_name="Fecha de Ingreso/Donación")
    estado = models.CharField(max_length=15, choices=ESTADOS, default='DISPONIBLE')
    aula_actual = models.CharField(max_length=100, blank=True, null=True)
    eliminado = models.BooleanField(default=False, editable=False)

    objects = EquipoManager()

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.serie}"


class Designacion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='historial')
    persona_responsable = models.CharField(max_length=150)
    aula_destino = models.CharField(max_length=100)
    fecha_entrega = models.DateTimeField(default=timezone.now)
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True)
    encargado_registro = models.ForeignKey(User, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.pk: # Al crear
            if self.equipo.estado != 'DISPONIBLE':
                raise ValidationError("El equipo no está disponible para asignación.")
            self.equipo.estado = 'EN_USO'
            self.equipo.aula_actual = self.aula_destino
            self.equipo.save()
        
        if self.fecha_devolucion_real: # Al devolver
            self.equipo.estado = 'DISPONIBLE'
            self.equipo.save() 
        super().save(*args, **kwargs)


class Estudiante(models.Model):
    NIVELES = [('PRI', 'Primaria'), ('SEC', 'Secundaria')]
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    
    nivel = models.CharField(max_length=3, choices=NIVELES)
    grado = models.CharField(max_length=10)
    seccion = models.CharField(max_length=1)
    
    padre = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hijas')

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

class Nota(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='notas')
    curso = models.CharField(max_length=100)
    b1 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    b2 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    b3 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    b4 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    promedio = models.DecimalField(max_digits=4, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.promedio = (self.b1 + self.b2 + self.b3 + self.b4) / 4
        super().save(*args, **kwargs)

class Asistencia(models.Model):
    ESTADOS = [('PRESENTE', 'Presente'), ('AUSENTE', 'Ausente'), ('TARDANZA', 'Tardanza')]
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS)

    class Meta:
        unique_together = ('estudiante', 'fecha')

class Comunicado(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    es_general = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Actividad(models.Model):
    TIPOS = [
        ('INTERNA', 'Interna del Colegio'),
        ('EXTERNA', 'Participación Externa (Desfiles/Concursos)'),
    ]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_actividad = models.DateTimeField()
    tipo = models.CharField(max_length=10, choices=TIPOS, default='INTERNA')

    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"