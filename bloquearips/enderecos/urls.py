from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_enderecos, name='listar_enderecos'),
    path('cadastrar/', views.cadastrar_endereco, name='cadastrar_endereco'),
    path('editar/<int:endereco_id>/', views.editar_endereco, name='editar_endereco'),
    path('excluir/<int:endereco_id>/', views.excluir_endereco, name='excluir_endereco'),
    path('<int:endereco_id>/', views.perfil_endereco, name='perfil_endereco'),
    path('massa/', views.massa_enderecos, name='massa_enderecos'),
]
