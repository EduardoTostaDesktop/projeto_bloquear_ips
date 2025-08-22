from django.urls import path
from . import views

app_name = "listas"

urlpatterns = [
    path('', views.listar_listas, name='listar_listas'),                # Lista todas as listas
    path('painel/', views.painel_listas, name='painel_listas'),        # Painel principal
    path('criar/', views.criar_lista, name='criar_lista'),            # Criar lista + upload CSV
    path('detalhar/<int:lista_id>/', views.detalhar_lista, name='detalhar_lista'),  # Detalhes da lista
    path('editar/<int:lista_id>/', views.editar_lista, name='editar_lista'),        # Editar lista
    path('excluir/<int:lista_id>/', views.excluir_lista, name='excluir_lista'),
    # ✅ URL para exclusão em massa
    path('excluir-massa/', views.excluir_listas_massa, name='excluir_listas_massa'),
]
