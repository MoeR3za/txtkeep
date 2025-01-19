from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Load snomeds in CTV3Hier table'
    
    def handle(self, *args, **options):
        if not User.objects.filter(username='reza').exists():
            print("creating user")
            u = User.objects.create(username="reza", email="reza@site.com")
            u.set_password("123456")
            u.save()
        else:
            print("user exists")