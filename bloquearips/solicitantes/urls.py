from django.urls import path
from . import views

app_name = "solicitantes"

urlpatterns = [
    path('', views.listar_solicitantes, name='listar_solicitantes'),             # Lista todos os solicitantes
    path('cadastrar/', views.cadastrar_solicitante, name='cadastrar_solicitante'),          # Cadastrar solicitante
    path('<int:solicitante_id>/', views.detalhar_solicitante, name='detalhar_solicitante'),  # Detalhes
    path('<int:solicitante_id>/editar/', views.editar_solicitante, name='editar_solicitante'), # Editar
]
