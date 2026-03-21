from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Seccion, Plazo
from datetime import date
from django.core.exceptions import ValidationError


@login_required
def dashboard(request):

    hoy = date.today()

    # 🔥 FILTRAR SOLO MES ACTUAL
    plazos = Plazo.objects.filter(
        fecha_limite__month=hoy.month,
        fecha_limite__year=hoy.year
    )

    # FILTRO POR USUARIO
    if request.user.is_superuser:
        secciones = Seccion.objects.all()
    else:
        secciones = Seccion.objects.filter(usuarios=request.user)

    # 🔥 CONTADORES CORRECTOS (SOLO MES ACTUAL)
    cumplidos = plazos.filter(estado="Cumplido").count()
    en_proceso = plazos.filter(estado="En proceso").count()
    pendientes = plazos.filter(
        estado="Pendiente",
        fecha_limite__gte=hoy
    ).count()

    vencidos = plazos.filter(
        estado__in=["Pendiente", "En proceso"],
        fecha_limite__lt=hoy
    ).count()

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

    hoy = date.today()

    seccion = Seccion.objects.get(id=id)

    # 🔥 SOLO MES ACTUAL
    plazos = Plazo.objects.filter(
        seccion=seccion,
        fecha_limite__month=hoy.month,
        fecha_limite__year=hoy.year
    )

    return render(request, "detalle_seccion.html", {
        "seccion": seccion,
        "plazos": plazos,
        "today": hoy
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