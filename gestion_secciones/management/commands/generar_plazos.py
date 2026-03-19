from django.core.management.base import BaseCommand
from gestion_secciones.models import Seccion, Plazo
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Genera plazos automáticamente'

    def handle(self, *args, **kwargs):

        hoy = date.today()
        mes = hoy.month
        año = hoy.year

        for seccion in Seccion.objects.all():

            # 🔹 MENSUAL
            self.crear_plazo(seccion, "Mensual", mes, año)

            # 🔹 TRIMESTRAL
            if mes in [3, 6, 9, 12]:
                self.crear_plazo(seccion, "Trimestral", mes, año)

            # 🔹 SEMESTRAL
            if mes in [6, 12]:
                self.crear_plazo(seccion, "Semestral", mes, año)

    def crear_plazo(self, seccion, tipo, mes, año):

        # Evitar duplicados
        if Plazo.objects.filter(
            seccion=seccion,
            tipo_plazo=tipo,
            fecha_limite__month=mes,
            fecha_limite__year=año
        ).exists():
            return

        # último día del mes
        if mes == 12:
            siguiente = date(año+1, 1, 1)
        else:
            siguiente = date(año, mes+1, 1)

        ultimo_dia = siguiente - timedelta(days=1)

        fecha_limite = ultimo_dia
        fecha_cumplimiento = ultimo_dia - timedelta(days=5)

        Plazo.objects.create(
            seccion=seccion,
            nombre_plazo=tipo,
            tipo_plazo=tipo,
            fecha_limite=fecha_limite,
            fecha_cumplimiento=fecha_cumplimiento,
            estado="Pendiente"
        )