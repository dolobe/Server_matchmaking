from django.contrib import admin
from .models import User, Role, UserRole, Game, Queue, Log, Match, Turn, MatchConfig, Session, Statistic

admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(Game)
admin.site.register(Queue)
admin.site.register(Log)
admin.site.register(Match)
admin.site.register(Turn)
admin.site.register(MatchConfig)
admin.site.register(Session)
admin.site.register(Statistic)