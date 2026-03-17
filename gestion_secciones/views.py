from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Seccion, Plazo
import datetime
from datetime import date
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

@login_required
def dashboard(request):

    mes_actual = datetime.datetime.now().month

    plazos = Plazo.objects.all()

    plazos_filtrados = []

    for plazo in plazos:

        if plazo.tipo_plazo == "Mensual":
            plazos_filtrados.append(plazo)

        elif plazo.tipo_plazo == "Trimestral":
            if mes_actual in [3, 6, 9, 12]:
                plazos_filtrados.append(plazo)

        elif plazo.tipo_plazo == "Semestral":
            if mes_actual in [6, 12]:
                plazos_filtrados.append(plazo)

    # FILTRO POR USUARIO
    if request.user.is_superuser:
        secciones = Seccion.objects.all()
    else:
        secciones = Seccion.objects.filter(usuarios=request.user)

    cumplidos = len([p for p in plazos_filtrados if p.estado == "Cumplido"])
    en_proceso = len([p for p in plazos_filtrados if p.estado == "En proceso"])
    pendientes = len([p for p in plazos_filtrados if p.estado == "Pendiente" and p.fecha_limite >= date.today()])
    vencidos = len([p for p in plazos_filtrados if p.estado != "Cumplido" and p.fecha_limite < date.today()])

    nombres_secciones = []
    porcentajes = []
    colores = []

    for s in secciones:

        porcentaje = s.porcentaje_cumplimiento()

        nombres_secciones.append(s.nombre_seccion)
        porcentajes.append(porcentaje)

        if porcentaje == 100:
            colores.append("green")
        elif porcentaje > 0:
            colores.append("orange")
        else:
            colores.append("red")

    return render(request, "dashboard.html", {
        "secciones": secciones,
        "cumplidos": cumplidos,
        "en_proceso": en_proceso,
        "pendientes": pendientes,
        "vencidos": vencidos,
        "nombres_secciones": nombres_secciones,
        "porcentajes": porcentajes,
        "colores": colores
    })

@login_required
def detalle_seccion(request, id):

    seccion = Seccion.objects.get(id=id)
    plazos = Plazo.objects.filter(seccion=seccion)

    return render(request, "detalle_seccion.html", {
        "seccion": seccion,
        "plazos": plazos,
        "today": date.today()
    })

@login_required
def historial(request):

    mes = request.GET.get('mes')
    seccion_id = request.GET.get('seccion')

    plazos = Plazo.objects.all()

    if mes:
        plazos = plazos.filter(fecha_limite__month=mes)

    if seccion_id:
        plazos = plazos.filter(seccion_id=seccion_id)

    secciones = Seccion.objects.all()

    return render(request, "historial.html", {
        "plazos": plazos,
        "secciones": secciones
    })

from django.shortcuts import redirect

@login_required
def editar_plazo(request, id):

    plazo = Plazo.objects.get(id=id)
    error = None

    if request.method == "POST":

        plazo.estado = request.POST.get("estado")
        plazo.radicado = request.POST.get("radicado")

        fecha = request.POST.get("fecha_cumplimiento")

        if fecha:
            plazo.fecha_cumplimiento = fecha

        try:
            plazo.full_clean()
            plazo.save()
            return redirect("detalle_seccion", id=plazo.seccion.id)

        except ValidationError as e:
            error = e

    return render(request, "editar_plazo.html", {
        "plazo": plazo,
        "error": error
    })

