from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError


class Seccion(models.Model):

    nombre_seccion = models.CharField(max_length=50)
    responsable = models.CharField(max_length=100)
    usuarios = models.ManyToManyField(User, blank=True)

    def porcentaje_cumplimiento(self):

        hoy = date.today()

        plazos = Plazo.objects.filter(
            seccion=self,
            fecha_limite__month=hoy.month,
            fecha_limite__year=hoy.year
        )

        total = plazos.count()
        cumplidos = plazos.filter(estado="Cumplido").count()

        if total == 0:
            return 0

        return int((cumplidos / total) * 100)

    def total_plazos(self):

        hoy = date.today()

        return Plazo.objects.filter(
            seccion=self,
            fecha_limite__month=hoy.month,
            fecha_limite__year=hoy.year
        ).count()

    def plazos_cumplidos(self):

        hoy = date.today()

        return Plazo.objects.filter(
            seccion=self,
            estado="Cumplido",
            fecha_limite__month=hoy.month,
            fecha_limite__year=hoy.year
        ).count()

    def __str__(self):
        return self.nombre_seccion


class Plazo(models.Model):

    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    nombre_plazo = models.CharField(max_length=200)

    tipo_plazo = models.CharField(
        max_length=20,
        choices=[
            ('Mensual', 'Mensual'),
            ('Trimestral', 'Trimestral'),
            ('Semestral', 'Semestral')
        ],
        default='Mensual'
    )

    periodo = models.DateField(null=True, blank=True)

    fecha_limite = models.DateField()
    fecha_cumplimiento = models.DateField(null=True, blank=True)

    radicado = models.CharField(
        max_length=16,
        blank=True,
        validators=[MinLengthValidator(16)]
    )

    estado = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En proceso', 'En proceso'),
            ('Cumplido', 'Cumplido')
        ],
        default='Pendiente'
    )

    def clean(self):

        if self.estado == "Cumplido":

            if not self.radicado or len(self.radicado) != 16:
                raise ValidationError(
                    "El radicado debe tener exactamente 16 caracteres cuando el plazo está cumplido"
                )

            if not self.fecha_cumplimiento:
                raise ValidationError(
                    "Debe ingresar la fecha de cumplimiento cuando el plazo está cumplido"
                )

    def save(self, *args, **kwargs):

        # ejecutar validaciones
        self.full_clean()

        hoy = date.today()

        # asignar periodo automáticamente (primer día del mes)
        if not self.periodo:
            self.periodo = date(hoy.year, hoy.month, 1)

        if self.estado != "Cumplido":
            if self.fecha_limite < hoy:
                self.estado = "Pendiente"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_plazo