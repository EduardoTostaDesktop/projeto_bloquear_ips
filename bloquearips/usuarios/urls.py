from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = "usuarios"
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

    # Solicitar reset de senha
    path('senha/reset/', auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset_form.html',
        email_template_name='usuarios/password_reset_email.html',
        subject_template_name='usuarios/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),

    # Página de sucesso após solicitar reset
    path('senha/reset/feito/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'
    ), name='password_reset_done'),

    # Página para digitar nova senha (clicando no link do email)
    path('senha/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    # Confirmação final
    path('senha/reset/feito/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'
    ), name='password_reset_complete'),
]
