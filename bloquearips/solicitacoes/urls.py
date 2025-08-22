from django.urls import path
from . import views

app_name = "solicitacoes"

urlpatterns = [
    path('', views.listar_solicitacoes, name='listar_solicitacoes'),
    path('criar/', views.criar_solicitacao, name='criar_solicitacao'),
    path('detalhar/<int:solicitacao_id>/', views.detalhar_solicitacao, name='detalhar_solicitacao'),
    path('excluir/<int:solicitacao_id>/', views.excluir_solicitacao, name='excluir_solicitacao'),
    path('excluir-massa/', views.excluir_solicitacoes_massa, name='excluir_solicitacoes_massa'),
]
