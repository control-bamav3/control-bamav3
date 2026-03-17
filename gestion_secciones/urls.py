from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('', views.dashboard, name='dashboard'),
    path('seccion/<int:id>/', views.detalle_seccion, name='detalle_seccion'),
    path('plazo/<int:id>/editar/', views.editar_plazo, name='editar_plazo'),
    path('historial/', views.historial, name='historial'),
]
