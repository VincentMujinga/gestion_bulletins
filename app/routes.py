# ==============================================================================
# Contenu COMPLET, VÉRIFIÉ ET CORRECT pour le fichier app/routes.py
# ==============================================================================

from flask import render_template, flash, redirect, url_for, request, current_app as app
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from app import db
import re
from datetime import datetime

# Imports des formulaires et modèles nécessaires pour tout le fichier
from app.forms import (LoginForm, AddUserForm, EditUserForm,
                       EtablissementForm, DemandeForm, RejectionForm)
from app.models import (User, Role, Etablissement,
                        Demande, LigneDemande, Notification)


# ==============================================================================
# DÉCORATEURS DE SÉCURITÉ
# ==============================================================================

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Administrateur':
            flash("Accès non autorisé.", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def chef_etablissement_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Chef d\'établissement':
            flash("Accès réservé.", 'danger')
            return redirect(url_for('dashboard'))
        if not current_user.etablissement:
            flash("Compte non associé à un établissement.", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def coordonnateur_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Coordonnateur':
            flash("Accès réservé.", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def sous_proved_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Sous-Proved':
            flash("Accès réservé.", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# ROUTES COMMUNES (Authentification, Dashboard, Notifications)
# ==============================================================================

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
            return redirect(request.args.get('next') or url_for('dashboard'))
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
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/notifications')
@login_required
def notifications():
    notifs_non_lues = current_user.notifications.filter_by(is_read=False).order_by(Notification.timestamp.desc())
    for notif in notifs_non_lues:
        notif.is_read = True
    db.session.commit()
    toutes_les_notifs = current_user.notifications.order_by(Notification.timestamp.desc()).all()
    return render_template('notifications.html', notifications=toutes_les_notifs, title="Mes Notifications")

def send_notification(user_id, message):
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)


# ==============================================================================
# ROUTES POUR LES DEMANDES (Chef d'Établissement & autres)
# ==============================================================================

@app.route('/demandes/nouvelle', methods=['GET', 'POST'])
@login_required
@chef_etablissement_required
def creer_demande():
    form = DemandeForm()
    options_par_type = {
        'Maternelle': {'niveaux': ['1ère', '2ème', '3ème'], 'options': {}},
        'Primaire': {'niveaux': ['Élémentaire', 'Moyen', '5ème', '6ème'], 'options': {}},
        'Secondaire': {
            'niveaux': ['7ème', '8ème'],
            'options': {
                'Pédagogie Générale': ['1ère', '2ème', '3ème', '4ème'], 'Coupe et Couture': ['1ère', '2ème', '3ème', '4ème'],
                'Scientifique': ['1ère', '2ème', '3ème', '4ème'], 'Mécanique Auto': ['1ère', '2ème', '3ème', '4ème'],
                'Commerciale et Gestion': ['1ère', '2ème', '3ème', '4ème'], 'Mécanique Générale': ['1ère', '2ème', '3ème', '4ème'],
                'Agronomie': ['1ère', '2ème', '3ème', '4ème'], 'Vétérinaire': ['1ère', '2ème', '3ème', '4ème'],
                'Électricité': ['1ère', '2ème', '3ème', '4ème']
            }
        }
    }
    if request.method == 'POST':
        annee_scolaire = request.form.get('annee_scolaire')
        lignes = []
        index = 0
        while f'lignes-{index}-type_ecole' in request.form:
            ligne_data = {
                'type_ecole': request.form.get(f'lignes-{index}-type_ecole'),
                'niveau_complet': request.form.get(f'lignes-{index}-niveau'),
                'quantite': request.form.get(f'lignes-{index}-quantite', 0, type=int)
            }
            if ligne_data['quantite'] > 0:
                lignes.append(ligne_data)
            index += 1
        if not annee_scolaire or not lignes:
            flash("Veuillez remplir l'année scolaire et ajouter au moins une ligne avec une quantité.", 'danger')
            return render_template('demandes/creer_demande.html', title="Nouvelle Demande", form=form, options_par_type=options_par_type)
        nouvelle_demande = Demande(annee_scolaire=annee_scolaire, etablissement_id=current_user.etablissement_id)
        db.session.add(nouvelle_demande)
        for data in lignes:
            niveau_val, option_val = data['niveau_complet'], None
            match = re.match(r"(.+?)\s\((.+)\)", niveau_val)
            if match:
                niveau_val, option_val = match.group(1).strip(), match.group(2).strip()
            ligne = LigneDemande(demande=nouvelle_demande, type_ecole=data['type_ecole'], niveau=niveau_val, option=option_val, quantite=data['quantite'])
            db.session.add(ligne)
        role_coordonnateur = Role.query.filter_by(name='Coordonnateur').first()
        if role_coordonnateur:
            tous_les_coordonnateurs = role_coordonnateur.users.all()
            db.session.flush()
            for coord in tous_les_coordonnateurs:
                message = f"Nouvelle demande (N°{nouvelle_demande.id}) de {current_user.etablissement.nom} à valider."
                send_notification(user_id=coord.id, message=message)
        db.session.commit()
        flash('Votre demande a été enregistrée et soumise avec succès.', 'success')
        return redirect(url_for('mes_demandes'))
    return render_template('demandes/creer_demande.html', title="Nouvelle Demande", form=form, options_par_type=options_par_type)

@app.route('/mes-demandes')
@login_required
@chef_etablissement_required
def mes_demandes():
    demandes = Demande.query.filter_by(etablissement_id=current_user.etablissement_id).order_by(Demande.date_demande.desc()).all()
    return render_template('demandes/mes_demandes.html', demandes=demandes, title="Mes Demandes")

@app.route('/demande/<int:demande_id>/details')
@login_required
def details_demande(demande_id):
    demande = Demande.query.get_or_404(demande_id)
    if current_user.role.name == 'Chef d\'établissement' and demande.etablissement_id != current_user.etablissement_id:
        flash("Accès non autorisé à cette demande.", 'danger')
        return redirect(url_for('mes_demandes'))
    form_rejet = RejectionForm()
    return render_template('demandes/details_demande.html', demande=demande, form_rejet=form_rejet, title=f"Détails Demande N°{demande.id}")


# ==============================================================================
# ROUTES POUR LE COORDONNATEUR
# ==============================================================================

@app.route('/coordonnateur/dashboard')
@login_required
@coordonnateur_required
def coordonnateur_dashboard():
    demandes_a_valider = Demande.query.filter_by(statut='Soumise').order_by(Demande.date_demande.asc()).all()
    stats = {
        'en_attente': len(demandes_a_valider),
        'traitees_par_moi': Demande.query.filter(
            Demande.processeur_id == current_user.id,
            Demande.statut.in_(['Validée', 'Rejetée'])
        ).count(),
        'total_recues': Demande.query.count()
    }
    return render_template('coordonnateur/dashboard.html', demandes=demandes_a_valider, stats=stats, title="Demandes à Valider")

@app.route('/coordonnateur/historique')
@login_required
@coordonnateur_required
def coordonnateur_historique():
    demandes_traitees = Demande.query.filter(
        Demande.processeur_id == current_user.id,
        Demande.statut.in_(['Validée', 'Rejetée'])
    ).order_by(Demande.date_traitement.desc()).all()
    return render_template('coordonnateur/historique.html', demandes=demandes_traitees, title="Historique des Traitements")

@app.route('/demande/<int:demande_id>/valider', methods=['POST'])
@login_required
@coordonnateur_required
def valider_demande(demande_id):
    demande = Demande.query.get_or_404(demande_id)
    if demande.statut == 'Soumise':
        demande.statut = 'Validée'
        demande.processeur_id = current_user.id
        demande.date_traitement = datetime.utcnow()
        chef = demande.etablissement.utilisateurs.first()
        if chef:
            message = f"Bonne nouvelle ! Votre demande N°{demande.id} a été VALIDÉE par le Coordonnateur."
            send_notification(user_id=chef.id, message=message)
        db.session.commit()
        flash(f'La demande N°{demande.id} a été validée avec succès.', 'success')
    else:
        flash(f'Cette demande n\'est plus en attente de validation.', 'warning')
    return redirect(url_for('coordonnateur_dashboard'))

@app.route('/demande/<int:demande_id>/rejeter', methods=['POST'])
@login_required
@coordonnateur_required
def rejeter_demande(demande_id):
    demande = Demande.query.get_or_404(demande_id)
    form = RejectionForm()
    if form.validate_on_submit():
        if demande.statut == 'Soumise':
            demande.statut = 'Rejetée'
            demande.processeur_id = current_user.id
            demande.date_traitement = datetime.utcnow()
            chef = demande.etablissement.utilisateurs.first()
            if chef:
                message = f"Attention : Votre demande N°{demande.id} a été REJETÉE. Motif : {form.motif_rejet.data}"
                send_notification(user_id=chef.id, message=message)
            db.session.commit()
            flash(f'La demande N°{demande.id} a été rejetée.', 'success')
        else:
            flash(f'Cette demande n\'est plus en attente de validation.', 'warning')
        return redirect(url_for('coordonnateur_dashboard'))
    else:
        flash('Le motif du rejet est obligatoire et doit faire au moins 10 caractères.', 'danger')
        return redirect(url_for('details_demande', demande_id=demande.id))


# ==============================================================================
# ROUTES POUR LE SOUS-PROVED
# ==============================================================================

# Dans app/routes.py

@app.route('/sous-proved/dashboard')
@login_required
@sous_proved_required
def sous_proved_dashboard():
    demandes_a_approuver = Demande.query.filter_by(statut='Validée').order_by(Demande.date_demande.asc()).all()

    # --- CALCUL DES STATS ---
    stats = {
        'en_attente': len(demandes_a_approuver),
        'traitees_par_moi': Demande.query.filter(
            Demande.processeur_id == current_user.id,
            Demande.statut.in_(['Approuvée', 'Rejetée'])
        ).count(),
        'total_validees': Demande.query.filter(Demande.statut.in_(['Validée', 'Approuvée', 'Traitée'])).count()
    }
    # --- FIN DU CALCUL ---

    # --- LIGNE CORRIGÉE ---
    return render_template('sous_proved/dashboard.html',
                           demandes=demandes_a_approuver,
                           stats=stats,  # <-- ON PASSE MAINTENANT LES STATS
                           title="Demandes à Approuver")
@app.route('/demande/<int:demande_id>/approuver', methods=['POST'])
@login_required
@sous_proved_required
def approuver_demande(demande_id):
    demande = Demande.query.get_or_404(demande_id)
    if demande.statut == 'Validée':
        coordonnateur_id = demande.processeur_id
        demande.statut = 'Approuvée'
        demande.processeur_id = current_user.id
        demande.date_traitement = datetime.utcnow()
        chef = demande.etablissement.utilisateurs.first()
        if chef:
            message_chef = f"Excellente nouvelle ! Votre demande N°{demande.id} a été APPROUVÉE par le Sous-Proved."
            send_notification(user_id=chef.id, message=message_chef)
        if coordonnateur_id:
            message_coord = f"Info : La demande N°{demande.id} que vous aviez validée a été approuvée."
            send_notification(user_id=coordonnateur_id, message=message_coord)
        db.session.commit()
        flash(f'La demande N°{demande.id} a été approuvée avec succès.', 'success')
    else:
        flash(f'Cette demande n\'est plus en attente d\'approbation.', 'warning')
    return redirect(url_for('sous_proved_dashboard'))

@app.route('/demande/<int:demande_id>/rejeter_sp', methods=['POST'])
@login_required
@sous_proved_required
def rejeter_demande_sp(demande_id):
    demande = Demande.query.get_or_404(demande_id)
    form = RejectionForm()
    if form.validate_on_submit():
        if demande.statut == 'Validée':
            coordonnateur_id = demande.processeur_id
            demande.statut = 'Rejetée'
            demande.processeur_id = current_user.id
            demande.date_traitement = datetime.utcnow()
            chef = demande.etablissement.utilisateurs.first()
            if chef:
                message_chef = f"Attention : Votre demande N°{demande.id} a été REJETÉE par le Sous-Proved. Motif : {form.motif_rejet.data}"
                send_notification(user_id=chef.id, message=message_chef)
            if coordonnateur_id:
                message_coord = f"Info : La demande N°{demande.id} que vous aviez validée a été rejetée."
                send_notification(user_id=coordonnateur_id, message=message_coord)
            db.session.commit()
            flash(f'La demande N°{demande.id} a été rejetée.', 'success')
        else:
            flash(f'Cette demande n\'est plus en attente d\'approbation.', 'warning')
        return redirect(url_for('sous_proved_dashboard'))
    else:
        flash('Le motif du rejet est obligatoire.', 'danger')
        return redirect(url_for('details_demande', demande_id=demande.id))


# Dans app/routes.py, à la suite des routes du Sous-Proved

@app.route('/sous-proved/historique')
@login_required
@sous_proved_required
def sous_proved_historique():
    """
    Affiche l'historique des demandes traitées par le Sous-Proved.
    """
    demandes_traitees = Demande.query.filter(
        Demande.processeur_id == current_user.id,
        Demande.statut.in_(['Approuvée', 'Rejetée'])
    ).order_by(Demande.date_traitement.desc()).all()

    return render_template('sous_proved/historique.html',
                           demandes=demandes_traitees,
                           title="Historique de mes Approbations")


# ==============================================================================
# ROUTES POUR L'ADMINISTRATEUR
# ==============================================================================

# --- Gestion des Utilisateurs ---
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
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Ce nom d\'utilisateur ou cet email est déjà utilisé.', 'danger')
        else:
            etablissement_id = form.etablissement.data if form.etablissement.data > 0 else None
            new_user = User(username=form.username.data, email=form.email.data, role_id=form.role.data, etablissement_id=etablissement_id)
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

# --- Gestion des Établissements ---
@app.route('/admin/etablissements')
@login_required
@admin_required
def list_etablissements():
    etablissements = Etablissement.query.order_by(Etablissement.nom).all()
    return render_template('admin/etablissements.html', etablissements=etablissements, title="Gestion des Établissements")

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
    form.nom.data = etablissement.nom
    form.ville.data = etablissement.ville
    form.cecop.data = etablissement.cecop
    return render_template('admin/edit_etablissement.html', form=form, title="Modifier l'Établissement")

@app.route('/admin/etablissements/delete/<int:etablissement_id>', methods=['POST'])
@login_required
@admin_required
def delete_etablissement(etablissement_id):
    etablissement = Etablissement.query.get_or_404(etablissement_id)
    db.session.delete(etablissement)
    db.session.commit()
    return redirect(url_for('list_etablissements'))