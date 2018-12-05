from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Utente, Commerciante, User


admin.site.register(Utente)
admin.site.register(Commerciante)
admin.site.register(User)
admin.site.unregister(Group)
