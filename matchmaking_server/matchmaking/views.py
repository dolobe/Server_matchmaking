import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import User, Role, UserRole, Queue, Match, Turn, Statistic
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
                        return redirect('home')
                    return redirect('home')
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
    is_admin = False
    stats = {
        "games_played": 0,
        "games_won": 0,
        "games_lost": 0,
        "games_draw": 0,
        "ia_wins": 0,
        "ia_loses": 0,
        "ia_draws": 0,
        "ia_wins_facile": 0,
        "ia_loses_facile": 0,
        "ia_draws_facile": 0,
        "ia_wins_moyen": 0,
        "ia_loses_moyen": 0,
        "ia_draws_moyen": 0,
        "ia_wins_difficile": 0,
        "ia_loses_difficile": 0,
        "ia_draws_difficile": 0,
    }
    if 'user_id' in request.session:
        try:
            user = User.objects.get(id=request.session['user_id'])
            is_admin = UserRole.objects.filter(user=user, role__name="admin").exists()
            logger.info(f"Dashboard affiché pour {user.username} (admin={is_admin})")
            # Récupérer les statistiques de l'utilisateur
            stats['games_played'] = Match.objects.filter(player1=user).count() + Match.objects.filter(player2=user).count()
            stats['games_won'] = Match.objects.filter(winner=user.username).count()
            games_draw = Match.objects.filter(winner="draw").filter(player1=user) | Match.objects.filter(winner="draw").filter(player2=user)
            stats['games_draw'] = games_draw.count()
            stats['games_lost'] = stats['games_played'] - stats['games_won'] - stats['games_draw']
            # Statistiques IA (toutes difficultés et par difficulté)
            try:
                stat = Statistic.objects.get(user=user)
                stats['ia_wins'] = stat.ia_wins
                stats['ia_loses'] = stat.ia_loses
                stats['ia_draws'] = stat.ia_draws
                stats['ia_wins_facile'] = stat.ia_wins_facile
                stats['ia_loses_facile'] = stat.ia_loses_facile
                stats['ia_draws_facile'] = stat.ia_draws_facile
                stats['ia_wins_moyen'] = stat.ia_wins_moyen
                stats['ia_loses_moyen'] = stat.ia_loses_moyen
                stats['ia_draws_moyen'] = stat.ia_draws_moyen
                stats['ia_wins_difficile'] = stat.ia_wins_difficile
                stats['ia_loses_difficile'] = stat.ia_loses_difficile
                stats['ia_draws_difficile'] = stat.ia_draws_difficile
            except Statistic.DoesNotExist:
                logger.info(f"Aucune statistique IA trouvée pour {user.username}, valeurs par défaut utilisées.")
        except User.DoesNotExist:
            logger.warning("Utilisateur non trouvé en session")
            user = None
    return render(request, "matchmaking/dashboard.html", {"user": user, "is_admin": is_admin, "stats": stats})

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
            stat, _ = Statistic.objects.get_or_create(user=user)
            return JsonResponse({
                "username": user.username,
                "email": user.email,
                "games_played": games_played,
                "games_won": games_won,
                "games_lost": games_lost,
                "games_draw": games_draw,
                "ia_wins": stat.ia_wins,
                "ia_loses": stat.ia_loses,
                "ia_draws": stat.ia_draws,
                "ia_wins_facile": stat.ia_wins_facile,
                "ia_loses_facile": stat.ia_loses_facile,
                "ia_draws_facile": stat.ia_draws_facile,
                "ia_wins_moyen": stat.ia_wins_moyen,
                "ia_loses_moyen": stat.ia_loses_moyen,
                "ia_draws_moyen": stat.ia_draws_moyen,
                "ia_wins_difficile": stat.ia_wins_difficile,
                "ia_loses_difficile": stat.ia_loses_difficile,
                "ia_draws_difficile": stat.ia_draws_difficile,
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({"detail": "Utilisateur inconnu."}, status=404)
    return JsonResponse({"detail": "Méthode non autorisée."}, status=405)

@csrf_exempt
def api_ia_match(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            result = data.get("result")  # "win", "lose", "draw"
            difficulty = data.get("difficulty", "facile")  # "facile", "moyen", "difficile"
            user = User.objects.get(username=username)
            stat, _ = Statistic.objects.get_or_create(user=user)
            # Global stats
            if result == "win":
                stat.ia_wins += 1
            elif result == "lose":
                stat.ia_loses += 1
            elif result == "draw":
                stat.ia_draws += 1
            # Stats par difficulté
            if difficulty == "facile":
                if result == "win":
                    stat.ia_wins_facile += 1
                elif result == "lose":
                    stat.ia_loses_facile += 1
                elif result == "draw":
                    stat.ia_draws_facile += 1
            elif difficulty == "moyen":
                if result == "win":
                    stat.ia_wins_moyen += 1
                elif result == "lose":
                    stat.ia_loses_moyen += 1
                elif result == "draw":
                    stat.ia_draws_moyen += 1
            elif difficulty == "difficile":
                if result == "win":
                    stat.ia_wins_difficile += 1
                elif result == "lose":
                    stat.ia_loses_difficile += 1
                elif result == "draw":
                    stat.ia_draws_difficile += 1
            stat.save()
            return JsonResponse({"detail": "Score IA enregistré."}, status=201)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=400)
    return JsonResponse({"detail": "Méthode non autorisée."}, status=405)
