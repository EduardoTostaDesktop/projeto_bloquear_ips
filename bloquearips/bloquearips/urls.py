from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='home'),
    path('usuarios/', include('usuarios.urls')), 
    path('enderecos/', include('enderecos.urls')),
    path('listas/', include('listas.urls')),  # Incluir URLs do app listas
    path('solicitantes/', include('solicitantes.urls')),  # Incluir URLs do app solicitantes
]
