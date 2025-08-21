from django.urls import path
from . import views

urlpatterns = [
    path('enderecos/painel/', views.painel_enderecos, name='painel_enderecos'),
    path('enderecos/', views.listar_enderecos, name='listar_enderecos'),
    path('enderecos/cadastrar/', views.cadastrar_endereco, name='cadastrar_endereco'),
    path('enderecos/editar/<int:endereco_id>/', views.editar_endereco, name='editar_endereco'),
    path('enderecos/excluir/<int:endereco_id>/', views.excluir_endereco, name='excluir_endereco'),
    path('<int:endereco_id>/', views.perfil_endereco, name='perfil_endereco'),
    path('massa/', views.massa_enderecos, name='massa_enderecos'),
]
