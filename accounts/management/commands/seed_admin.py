import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Cria ou atualiza o superusuário a partir de variáveis de ambiente.

    Útil em plataformas sem Shell (ex.: Render no plano free), onde o admin
    precisa ser criado durante o build/deploy.
    """

    help = "Cria ou atualiza o superusuário usando DJANGO_SUPERUSER_*."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not username or not password:
            raise CommandError(
                "Defina as variáveis DJANGO_SUPERUSER_USERNAME e "
                "DJANGO_SUPERUSER_PASSWORD."
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "perfil": "coordenadora"},
        )

        user.email = email or user.email
        user.perfil = "coordenadora"
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "criado" if created else "atualizado"
        self.stdout.write(
            self.style.SUCCESS(f"Superusuário '{username}' {action} com sucesso.")
        )
