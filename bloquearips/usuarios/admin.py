from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informações pessoais", {"fields": ("first_name", "last_name", "email")}),
        ("Tipo de usuário", {"fields": ("tipo",)}),  # 👈 AQUI
        ("Permissões", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Datas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "tipo",          # 👈 E AQUI
                "password1",
                "password2",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    list_display = ("username", "email", "tipo", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("username",)
