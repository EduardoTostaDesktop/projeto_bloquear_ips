from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('lista/', views.lista_usuarios, name='lista_usuarios'),
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
    path("excluir-massa/", views.excluir_usuarios_massa, name="excluir_usuarios_massa"),  # <- NOVA ROTA
    # Perfil do próprio usuário
    path("perfil/", views.perfil, name="perfil"),

    # Perfil de outro usuário (somente admins)
    path("perfil/<int:usuario_id>/", views.perfil, name="perfil_usuario"),
    path("perfil/alterar-senha/", views.alterar_senha, name="alterar_senha"),

]
