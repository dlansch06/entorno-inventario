"""
URL configuration for sistema_colegio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from inventario import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('invitado/', views.invitado_view, name='invitado'),

    
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('consulta-notas/', views.notas_view, name='notas'),
    path('consulta-asistencias/', views.asistencias_view, name='asistencias'),
    path('registro-padre/', views.registro_padre_view, name='registro_padre'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('equipos/', views.inventario_view, name='inventario'),
    path('acerca-del-colegio/', views.acerca_de_view, name='info'),
    
    path('equipos/eliminar/<int:pk>/', views.mover_a_papelera, name='mover_a_papelera'),
    path('papelera/', views.ver_papelera, name='ver_papelera'),
    path('papelera/restaurar/<int:pk>/', views.restaurar_equipo, name='restaurar_equipo'),
    path('papelera/borrar-definitivo/<int:pk>/', views.eliminar_permanente, name='eliminar_permanente'),
    path('logout/', views.logout_view, name='logout'),
]