from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseForbidden
from .models import (
    User, Role, UserRole, UserManager, Game, Queue, Log,
    MatchConfig, Match, Turn, Session, Statistic
)

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Si le mot de passe n'est pas déjà hashé, on le hash
        if password and not password.startswith('pbkdf2_'):
            return make_password(password)
        return password

class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

    def has_module_permission(self, request):
        # Autorise seulement les utilisateurs ayant le rôle "admin"
        if not request.user.is_authenticated:
            return False
        try:
            # Ici, request.user est un User Django natif, pas ton modèle User personnalisé
            # Donc on vérifie le username dans ta table User
            from .models import User, UserRole
            user = User.objects.filter(username=request.user.username).first()
            if not user:
                return False
            return UserRole.objects.filter(user=user, role__name="admin").exists()
        except Exception:
            return False

admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(UserManager)
admin.site.register(Game)
admin.site.register(Queue)
admin.site.register(Log)
admin.site.register(MatchConfig)
admin.site.register(Match)
admin.site.register(Turn)
admin.site.register(Session)
admin.site.register(Statistic)
