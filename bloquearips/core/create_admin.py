import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and email and password:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "tipo": "admin",
            "is_staff": True,
            "is_superuser": True,
        },
    )

    if created:
        user.set_password(password)
        user.save()
        print("Superuser administrador criado com sucesso!")
    else:
        # 🔥 Atualiza caso já exista
        user.tipo = "admin"
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        print("Superuser atualizado para administrador!")