# ==============================================================================
# Contenu COMPLET et CORRECT pour le fichier app/routes.py
# Étape : Ajout de la création de demande pour le Chef d'Établissement
# ==============================================================================

from flask import render_template, flash, redirect, url_for, request, current_app as app
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from app import db
import re
# On importe tous les formulaires et modèles nécessaires en une seule fois
from app.forms import LoginForm, AddUserForm, EditUserForm, EtablissementForm, DemandeForm
from app.models import User, Role, Etablissement, Demande, LigneDemande


# --- Section des Décorateurs de Sécurité ---

def admin_required(f):
    """Décorateur pour les routes réservées à l'administrateur."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Administrateur':
            flash("Accès non autorisé. Vous devez être administrateur.", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated_function


def chef_etablissement_required(f):
    """Décorateur pour les routes réservées au Chef d'établissement."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Chef d\'établissement':
            flash("Accès réservé aux chefs d'établissement.", 'danger')
            return redirect(url_for('dashboard'))
        if not current_user.etablissement:
            flash("Votre compte n'est pas associé à un établissement. Contactez l'administrateur.", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated_function


# --- Routes d'Authentification et de Navigation de Base ---

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Identifiants invalides.', 'danger')
    return render_template('auth/login.html', form=form, title="Connexion")


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title="Tableau de Bord")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('login'))


# --- Routes pour le Chef d'Établissement ---

# Dans app/routes.py

# Dans app/routes.py

  # <-- Assurez-vous d'importer 're' en haut de votre fichier


# ... (gardez tous les autres imports et les autres routes) ...

@app.route('/demandes/nouvelle', methods=['GET', 'POST'])
@login_required
@chef_etablissement_required
def creer_demande():
    # On passe le formulaire vide à la page pour la protection CSRF
    form = DemandeForm()

    # On définit la structure des options pour le JavaScript
    options_par_type = {
        'Maternelle': {
            'niveaux': ['1ère', '2ème', '3ème'],
            'options': {}
        },
        'Primaire': {
            'niveaux': ['Élémentaire', 'Moyen', '5ème', '6ème'],
            'options': {}
        },
        'Secondaire': {
            'niveaux': ['7ème', '8ème'],
            'options': {
                'Pédagogie Générale': ['1ère', '2ème', '3ème', '4ème'],
                'Coupe et Couture': ['1ère', '2ème', '3ème', '4ème'],
                'Scientifique': ['1ère', '2ème', '3ème', '4ème'],
                'Mécanique Auto': ['1ère', '2ème', '3ème', '4ème'],
                'Commerciale et Gestion': ['1ère', '2ème', '3ème', '4ème'],
                'Mécanique Générale': ['1ère', '2ème', '3ème', '4ème'],
                'Agronomie': ['1ère', '2ème', '3ème', '4ème'],
                'Vétérinaire': ['1ère', '2ème', '3ème', '4ème'],
                'Électricité': ['1ère', '2ème', '3ème', '4ème']
            }
        }
    }

    # --- DÉBUT DE LA LOGIQUE DE SAUVEGARDE CORRIGÉE ---
    if request.method == 'POST':
        # On récupère les données manuellement car le formulaire est dynamique
        annee_scolaire = request.form.get('annee_scolaire')
        lignes = []

        # Le formulaire dynamique envoie les champs sous la forme 'lignes-0-type_ecole', 'lignes-1-type_ecole', etc.
        # Nous devons parser ces données.
        index = 0
        while f'lignes-{index}-type_ecole' in request.form:
            ligne_data = {
                'type_ecole': request.form.get(f'lignes-{index}-type_ecole'),
                'niveau_complet': request.form.get(f'lignes-{index}-niveau'),
                'quantite': request.form.get(f'lignes-{index}-quantite', 0, type=int)
            }
            lignes.append(ligne_data)
            index += 1

        if not annee_scolaire or not lignes:
            flash("Veuillez remplir l'année scolaire et ajouter au moins une ligne à votre demande.", 'danger')
            return render_template('demandes/creer_demande.html', title="Nouvelle Demande", form=form,
                                   options_par_type=options_par_type)

        # 1. Créer l'objet Demande principal
        nouvelle_demande = Demande(
            annee_scolaire=annee_scolaire,
            etablissement_id=current_user.etablissement_id,
            statut='Soumise'
        )
        db.session.add(nouvelle_demande)

        # 2. Créer chaque objet LigneDemande et le lier à la Demande
        for data in lignes:
            niveau_val = data['niveau_complet']
            option_val = None

            # On utilise une expression régulière pour extraire le niveau et l'option
            # si le format est "Niveau (Option)"
            match = re.match(r"(.+?)\s\((.+)\)", niveau_val)
            if match:
                niveau_val = match.group(1).strip()  # Ex: "3ème"
                option_val = match.group(2).strip()  # Ex: "Scientifique"

            ligne = LigneDemande(
                demande=nouvelle_demande,  # Relation SQLAlchemy
                type_ecole=data['type_ecole'],
                niveau=niveau_val,
                option=option_val,
                quantite=data['quantite']
            )
            db.session.add(ligne)

        # 3. Sauvegarder tout dans la base de données
        db.session.commit()

        flash('Votre demande a été enregistrée et soumise avec succès.', 'success')
        return redirect(url_for('dashboard'))
    # --- FIN DE LA LOGIQUE DE SAUVEGARDE CORRIGÉE ---

    return render_template('demandes/creer_demande.html', title="Nouvelle Demande", form=form,
                           options_par_type=options_par_type)    # --- FIN DE LA MODIFICATION ---

    if form.validate_on_submit():
        # ... (la logique de soumission reste la même) ...
        # ...
        flash('Votre demande a été soumise avec succès.', 'success')
        return redirect(url_for('dashboard'))

    # On passe les options au template
    return render_template('demandes/creer_demande.html', title="Nouvelle Demande", form=form,
                           options_par_type=options_par_type)
# --- Routes de la Section Administration ---

@app.route('/admin/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users, title="Gestion des Utilisateurs")


@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Ce nom d\'utilisateur ou cet email est déjà utilisé.', 'danger')
        else:
            etablissement_id = form.etablissement.data if form.etablissement.data > 0 else None
            new_user = User(username=form.username.data, email=form.email.data, role_id=form.role.data,
                            etablissement_id=etablissement_id)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Utilisateur créé avec succès!', 'success')
            return redirect(url_for('list_users'))
    return render_template('admin/add_user.html', form=form, title="Ajouter un Utilisateur")


@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        user.etablissement_id = form.etablissement.data if form.etablissement.data > 0 else None
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Les informations de l\'utilisateur ont été mises à jour.', 'success')
        return redirect(url_for('list_users'))
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role_id
    form.etablissement.data = user.etablissement_id or 0
    return render_template('admin/edit_user.html', form=form, user=user, title="Modifier l'Utilisateur")


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte administrateur.', 'danger')
        return redirect(url_for('list_users'))
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('list_users'))


@app.route('/admin/etablissements')
@login_required
@admin_required
def list_etablissements():
    etablissements = Etablissement.query.order_by(Etablissement.nom).all()
    return render_template('admin/etablissements.html', etablissements=etablissements,
                           title="Gestion des Établissements")


@app.route('/admin/etablissements/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_etablissement():
    form = EtablissementForm()
    if form.validate_on_submit():
        existing = Etablissement.query.filter_by(nom=form.nom.data).first()
        if existing:
            flash('Un établissement avec ce nom existe déjà.', 'danger')
        else:
            new_etablissement = Etablissement(nom=form.nom.data, ville=form.ville.data, cecop=form.cecop.data)
            db.session.add(new_etablissement)
            db.session.commit()
            flash('Nouvel établissement créé avec succès.', 'success')
            return redirect(url_for('list_etablissements'))
    return render_template('admin/add_etablissement.html', form=form, title="Ajouter un Établissement")


@app.route('/admin/etablissements/edit/<int:etablissement_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_etablissement(etablissement_id):
    etablissement = Etablissement.query.get_or_404(etablissement_id)
    form = EtablissementForm(obj=etablissement)
    if form.validate_on_submit():
        etablissement.nom = form.nom.data
        etablissement.ville = form.ville.data
        etablissement.cecop = form.cecop.data
        db.session.commit()
        flash('Établissement mis à jour avec succès.', 'success')
        return redirect(url_for('list_etablissements'))
    return render_template('admin/edit_etablissement.html', form=form, title="Modifier l'Établissement")


@app.route('/admin/etablissements/delete/<int:etablissement_id>', methods=['POST'])
@login_required
@admin_required
def delete_etablissement(etablissement_id):
    etablissement = Etablissement.query.get_or_404(etablissement_id)
    db.session.delete(etablissement)
    db.session.commit()
    return redirect(url_for('list_etablissements'))