import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import User, Role, UserRole, Queue, Match, Turn
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)

def register_view(request):
    logger.info("Accès à la page d'inscription")
    if request.method == 'POST':
        logger.info("Formulaire d'inscription soumis")
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            logger.info(f"Tentative d'inscription pour {username}")
            if User.objects.filter(username=username).exists():
                logger.warning(f"Inscription échouée : {username} existe déjà")
                messages.error(request, "Ce nom d'utilisateur existe déjà.")
            else:
                try:
                    user = User(username=username, email=email)
                    user.password = make_password(password)
                    logger.info(f"Mot de passe hashé pour {username}: {user.password}")
                    user.save()
                    role, _ = Role.objects.get_or_create(name="user")
                    UserRole.objects.create(user=user, role=role)
                    logger.info(f"Inscription réussie pour {username}")
                    messages.success(request, "Inscription réussie. Connectez-vous.")
                    return redirect('login')
                except Exception as e:
                    logger.error(f"Erreur lors de l'inscription de {username}: {e}")
                    messages.error(request, "Erreur lors de l'inscription.")
        else:
            logger.warning("Formulaire d'inscription invalide")
    else:
        form = RegisterForm()
    return render(request, 'matchmaking/register.html', {'form': form})

def login_view(request):
    logger.info("Accès à la page de connexion")
    if request.method == 'POST':
        logger.info("Formulaire de connexion soumis")
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            logger.info(f"Tentative de connexion pour {username}")
            try:
                user = User.objects.get(username=username)
                if check_password(password, getattr(user, 'password', '')):
                    request.session['user_id'] = user.id
                    is_admin = UserRole.objects.filter(user=user, role__name="admin").exists()
                    logger.info(f"Connexion réussie pour {username} (admin={is_admin})")
                    if is_admin:
                        return redirect('admin_dashboard')
                    return redirect('dashboard')
                else:
                    logger.warning(f"Mot de passe incorrect pour {username}")
                    messages.error(request, "Mot de passe incorrect.")
            except User.DoesNotExist:
                logger.warning(f"Utilisateur inconnu : {username}")
                messages.error(request, "Utilisateur inconnu.")
            except Exception as e:
                logger.error(f"Erreur lors de la connexion de {username}: {e}")
                messages.error(request, "Erreur lors de la connexion.")
        else:
            logger.warning("Formulaire de connexion invalide")
    else:
        form = LoginForm()
    return render(request, 'matchmaking/login.html', {'form': form})

def logout_view(request):
    logger.info("Déconnexion utilisateur")
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')

def dashboard_view(request):
    logger.info("Accès au dashboard utilisateur")
    user = None
    if 'user_id' in request.session:
        try:
            user = User.objects.get(id=request.session['user_id'])
            logger.info(f"Dashboard affiché pour {user.username}")
        except User.DoesNotExist:
            logger.warning("Utilisateur non trouvé en session")
            user = None
    return render(request, 'matchmaking/dashboard.html', {'user': user})

def admin_dashboard_view(request):
    logger.info("Accès au dashboard admin")
    user = None
    if 'user_id' in request.session:
        try:
            user = User.objects.get(id=request.session['user_id'])
            is_admin = UserRole.objects.filter(user=user, role__name="admin").exists()
            if not is_admin:
                logger.warning(f"Accès admin refusé pour {user.username}")
                return redirect('dashboard')
            logger.info(f"Dashboard admin affiché pour {user.username}")
        except User.DoesNotExist:
            logger.warning("Utilisateur non trouvé en session (admin)")
            return redirect('login')
    else:
        logger.warning("Tentative d'accès admin sans session")
        return redirect('login')
    queues = Queue.objects.all()
    matchs = Match.objects.all()
    turns = Turn.objects.all()
    return render(request, 'matchmaking/admin_dashboard.html', {
        'user': user,
        'queues': queues,
        'matchs': matchs,
        'turns': turns,
    })

def home_view(request):
    logger.info("Accès à la page d'accueil")
    user = None
    is_admin = False
    if 'user_id' in request.session:
        try:
            user = User.objects.get(id=request.session['user_id'])
            is_admin = user.userrole_set.filter(role__name="admin").exists()
            logger.info(f"Accueil affiché pour {user.username} (admin={is_admin})")
        except User.DoesNotExist:
            logger.warning("Utilisateur non trouvé en session (home)")
            user = None
    queue_count = Queue.objects.count()
    match_count = Match.objects.filter(is_finished=False).count()
    logger.info(f"Stats accueil : {queue_count} en file, {match_count} matchs en cours")
    return render(request, 'matchmaking/home.html', {
        'user': user,
        'queue_count': queue_count,
        'match_count': match_count,
        'is_admin': is_admin,
    })

@csrf_exempt
def api_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            email = data.get("email", "")
            if not username or not password:
                return JsonResponse({"detail": "Champs requis manquants."}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"detail": "Nom d'utilisateur déjà pris."}, status=400)
            user = User(username=username, email=email, password=make_password(password))
            user.save()
            return JsonResponse({"username": user.username, "email": user.email}, status=201)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=400)
    return JsonResponse({"detail": "Méthode non autorisée."}, status=405)

@csrf_exempt
def api_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                return JsonResponse({"detail": "Champs requis manquants."}, status=400)
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    return JsonResponse({"username": user.username, "email": user.email}, status=200)
                else:
                    return JsonResponse({"detail": "Mot de passe incorrect."}, status=401)
            except User.DoesNotExist:
                return JsonResponse({"detail": "Utilisateur inconnu."}, status=401)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=400)
    return JsonResponse({"detail": "Méthode non autorisée."}, status=405)

@csrf_exempt
def api_stats(request, username):
    if request.method == "GET":
        try:
            user = User.objects.get(username=username)
            games_played = Match.objects.filter(player1=user).count() + Match.objects.filter(player2=user).count()
            games_won = Match.objects.filter(winner=username).count()
            games_draw = Match.objects.filter(winner="draw").filter(player1=user) | Match.objects.filter(winner="draw").filter(player2=user)
            games_draw = games_draw.count()
            games_lost = games_played - games_won - games_draw
            return JsonResponse({
                "username": user.username,
                "email": user.email,
                "games_played": games_played,
                "games_won": games_won,
                "games_lost": games_lost,
                "games_draw": games_draw,
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({"detail": "Utilisateur inconnu."}, status=404)
    return JsonResponse({"detail": "Méthode non autorisée."}, status=405)
