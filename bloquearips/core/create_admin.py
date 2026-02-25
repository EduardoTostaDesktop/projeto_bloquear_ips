import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and email and password:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        # 👇 ajuste o nome do campo se for diferente
        user.tipo = "admin"
        user.save()

        print("Superuser administrador criado com sucesso!")
    else:
        print("Superuser já existe.")