from django.core.management.base import BaseCommand
from gestion_secciones.models import Plazo
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Genera plazos automáticamente'

    def handle(self, *args, **kwargs):

        hoy = date.today()

        # calcular siguiente mes
        if hoy.month == 12:
            mes = 1
            año = hoy.year + 1
        else:
            mes = hoy.month + 1
            año = hoy.year

        # traer plazos actuales
        plazos_actuales = Plazo.objects.filter(
            fecha_limite__month=hoy.month,
            fecha_limite__year=hoy.year
        )

        for plazo in plazos_actuales:

            # evitar duplicados
            if Plazo.objects.filter(
                seccion=plazo.seccion,
                nombre_plazo=plazo.nombre_plazo,
                fecha_limite__month=mes,
                fecha_limite__year=año
            ).exists():
                continue

            # calcular último día del mes
            if mes == 12:
                siguiente = date(año+1, 1, 1)
            else:
                siguiente = date(año, mes+1, 1)

            ultimo_dia = siguiente - timedelta(days=1)

            fecha_limite = ultimo_dia
            fecha_cumplimiento = ultimo_dia - timedelta(days=5)

            # crear nuevo plazo
            Plazo.objects.create(
                seccion=plazo.seccion,
                nombre_plazo=plazo.nombre_plazo,
                tipo_plazo=plazo.tipo_plazo,
                fecha_limite=fecha_limite,
                fecha_cumplimiento=fecha_cumplimiento,
                estado="Pendiente"
            )