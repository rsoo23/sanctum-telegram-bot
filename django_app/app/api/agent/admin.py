from django.contrib import admin

# Register your models here.
from api.agent.models import Agent

admin.site.register(Agent)
