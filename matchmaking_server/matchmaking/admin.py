from django.contrib import admin
from .models import User, Queue, Match, Turn

admin.site.register(User)
admin.site.register(Queue)
admin.site.register(Match)
admin.site.register(Turn)
