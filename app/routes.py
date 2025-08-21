# ==============================================================================
# Contenu COMPLET, UNIQUE ET FINAL pour le fichier app/routes.py
# ==============================================================================

from flask import render_template, flash, redirect, url_for, request, current_app as app
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from app import db
import re
from datetime import datetime
# En haut de app/routes.py
import subprocess
import os
from flask import send_from_directory

# Imports des formulaires et modèles nécessaires pour tout le fichier
from app.forms import (LoginForm, AddUserForm, EditUserForm,
                       EtablissementForm, DemandeForm, RejectionForm)
from app.models import (User, Role, Etablissement,
                        Demande, LigneDemande, Notification, Log)


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

def proved_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Proved':
            flash("Accès réservé.", 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
# ==============================================================================
# ROUTES COMMUNES
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


# ==============================================================================
# ROUTES COMMUNES (Authentification, Dashboard, Notifications)
# ==============================================================================

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
# ROUTES POUR LE WORKFLOW DE VALIDATION
# ==============================================================================

# --- Coordonnateur ---
@app.route('/coordonnateur/dashboard')
@login_required
@coordonnateur_required
def coordonnateur_dashboard():
    demandes_a_valider = Demande.query.filter_by(statut='Soumise').order_by(Demande.date_demande.asc()).all()
    stats = {
        'en_attente': len(demandes_a_valider),
        'traitees_par_moi': Demande.query.filter(Demande.processeur_id == current_user.id, Demande.statut.in_(['Validée', 'Rejetée'])).count(),
        'total_recues': Demande.query.count()
    }
    return render_template('coordonnateur/dashboard.html', demandes=demandes_a_valider, stats=stats, title="Demandes à Valider")

@app.route('/coordonnateur/historique')
@login_required
@coordonnateur_required
def coordonnateur_historique():
    demandes_traitees = Demande.query.filter(Demande.processeur_id == current_user.id, Demande.statut.in_(['Validée', 'Rejetée'])).order_by(Demande.date_traitement.desc()).all()
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
            send_notification(chef.id, f"Bonne nouvelle ! Votre demande N°{demande.id} a été VALIDÉE par le Coordonnateur.")
        role_sous_proved = Role.query.filter_by(name='Sous-Proved').first()
        if role_sous_proved:
            for sp in role_sous_proved.users.all():
                send_notification(sp.id, f"Nouvelle demande (N°{demande.id}) de {demande.etablissement.nom} à approuver.")
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
                send_notification(chef.id, f"Attention : Votre demande N°{demande.id} a été REJETÉE. Motif : {form.motif_rejet.data}")
            db.session.commit()
            flash(f'La demande N°{demande.id} a été rejetée.', 'success')
        else:
            flash(f'Cette demande n\'est plus en attente de validation.', 'warning')
        return redirect(url_for('coordonnateur_dashboard'))
    else:
        flash('Le motif du rejet est obligatoire.', 'danger')
        return redirect(url_for('details_demande', demande_id=demande.id))

# --- Sous-Proved ---
@app.route('/sous-proved/dashboard')
@login_required
@sous_proved_required
def sous_proved_dashboard():
    demandes_a_approuver = Demande.query.filter_by(statut='Validée').order_by(Demande.date_demande.asc()).all()
    stats = {
        'en_attente': len(demandes_a_approuver),
        'traitees_par_moi': Demande.query.filter(Demande.processeur_id == current_user.id, Demande.statut.in_(['Approuvée', 'Rejetée'])).count(),
        'total_validees': Demande.query.filter(Demande.statut.in_(['Validée', 'Approuvée', 'Traitée'])).count()
    }
    return render_template('sous_proved/dashboard.html', demandes=demandes_a_approuver, stats=stats, title="Demandes à Approuver")

@app.route('/sous-proved/historique')
@login_required
@sous_proved_required
def sous_proved_historique():
    demandes_traitees = Demande.query.filter(Demande.processeur_id == current_user.id, Demande.statut.in_(['Approuvée', 'Rejetée'])).order_by(Demande.date_traitement.desc()).all()
    return render_template('sous_proved/historique.html', demandes=demandes_traitees, title="Historique de mes Approbations")

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
            send_notification(chef.id, f"Excellente nouvelle ! Votre demande N°{demande.id} a été APPROUVÉE par le Sous-Proved.")
        if coordonnateur_id:
            send_notification(coordonnateur_id, f"Info : La demande N°{demande.id} que vous aviez validée a été approuvée.")
        role_proved = Role.query.filter_by(name='Proved').first()
        if role_proved:
            for proved in role_proved.users.all():
                send_notification(proved.id, f"Nouvelle demande (N°{demande.id}) de {demande.etablissement.nom} à traiter.")
                # À l'intérieur de la fonction approuver_demande(), dans le "if demande.statut == 'Validée':"

                # ... (après avoir notifié le chef et le coordonnateur)

                # 3. Notifier tous les Proved
                role_proved = Role.query.filter_by(name='Proved').first()
                if role_proved:
                    tous_les_proved = role_proved.users.all()
                    for proved in tous_les_proved:
                        message_proved = f"Nouvelle demande (N°{demande.id}) de {demande.etablissement.nom} attend votre traitement."
                        send_notification(user_id=proved.id, message=message_proved)
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
                send_notification(chef.id, f"Attention : Votre demande N°{demande.id} a été REJETÉE par le Sous-Proved. Motif : {form.motif_rejet.data}")
            if coordonnateur_id:
                send_notification(coordonnateur_id, f"Info : La demande N°{demande.id} que vous aviez validée a été rejetée.")
            db.session.commit()
            flash(f'La demande N°{demande.id} a été rejetée.', 'success')
        else:
            flash(f'Cette demande n\'est plus en attente d\'approbation.', 'warning')
        return redirect(url_for('sous_proved_dashboard'))
    else:
        flash('Le motif du rejet est obligatoire.', 'danger')
        return redirect(url_for('details_demande', demande_id=demande.id))


# --- Routes pour le Proved ---

@app.route('/proved/dashboard')
@login_required
@proved_required
def proved_dashboard():
    """
    Affiche le tableau de bord du Proved avec les demandes à traiter.
    """
    demandes_a_traiter = Demande.query.filter_by(statut='Approuvée') \
        .order_by(Demande.date_demande.asc()).all()
    return render_template('proved/dashboard.html',
                           demandes=demandes_a_traiter,
                           title="Demandes à Traiter")


@app.route('/demande/<int:demande_id>/traiter', methods=['POST'])
@login_required
@proved_required
def traiter_demande(demande_id):
    """
    Change le statut d'une demande de 'Approuvée' à 'Traitée'.
    """
    demande = Demande.query.get_or_404(demande_id)
    if demande.statut == 'Approuvée':
        demande.statut = 'Traitée'
        demande.processeur_id = current_user.id
        demande.date_traitement = datetime.utcnow()

        # Notifier le Chef d'établissement que sa commande est prête
        chef = demande.etablissement.utilisateurs.first()
        if chef:
            message = f"Votre demande N°{demande.id} a été TRAITÉE. Les bulletins sont prêts pour la distribution."
            send_notification(user_id=chef.id, message=message)

        # Ici, plus tard, on ajoutera la logique pour déduire du stock

        db.session.commit()
        flash(f'La demande N°{demande.id} a été marquée comme traitée.', 'success')
    else:
        flash(f'Cette demande n\'est plus en attente de traitement.', 'warning')

    return redirect(url_for('proved_dashboard'))

# --- Proved ---

# ==============================================================================
# ROUTES POUR L'ADMINISTRATEUR
# ==============================================================================
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
        nom = form.nom.data
        ville = form.ville.data
        cecop = form.cecop.data

        # Vérification de l'unicité du nom
        if Etablissement.query.filter_by(nom=nom).first():
            flash('Un établissement avec ce nom existe déjà.', 'danger')
            return render_template('admin/add_etablissement.html', form=form, title="Ajouter un Établissement")

        # Vérification de l'unicité du N° CECOP SEULEMENT s'il n'est pas vide
        if cecop and Etablissement.query.filter_by(cecop=cecop).first():
            flash('Un établissement avec ce N° CECOP existe déjà.', 'danger')
            return render_template('admin/add_etablissement.html', form=form, title="Ajouter un Établissement")

        # Si tout est bon, on crée
        new_etablissement = Etablissement(nom=nom, ville=ville, cecop=cecop)
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


# Dans app/routes.py, avec les autres routes admin

@app.route('/admin/backup')
@login_required
@admin_required
def backup_db():
    """
    Crée une sauvegarde de la base de données et la propose en téléchargement.
    """
    try:
        # Nom du fichier de sauvegarde avec la date
        backup_filename = f"backup_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.sql"
        # Chemin complet où sauvegarder le fichier
        backup_path = os.path.join(app.root_path, '..',
                                   'backups')  # On sauvegarde dans un dossier 'backups' à la racine

        # Créer le dossier 'backups' s'il n'existe pas
        os.makedirs(backup_path, exist_ok=True)

        full_backup_path = os.path.join(backup_path, backup_filename)

        # Construction de la commande mysqldump
        # ATTENTION : 'mysqldump' doit être accessible dans le PATH du système.
        # C'est généralement le cas avec une installation standard de XAMPP/WAMP/MySQL.
        command = [
            'mysqldump',
            f'--host={app.config["DB_HOST"]}',
            f'--user={app.config["DB_USER"]}',
            f'--password={app.config["DB_PASSWORD"]}',
            app.config["DB_NAME"],
            f'--result-file={full_backup_path}'
        ]

        # Exécution de la commande
        subprocess.run(command, check=True)

        flash('Sauvegarde de la base de données créée avec succès.', 'success')
        # Proposer le fichier en téléchargement
        return send_from_directory(directory=backup_path, path=backup_filename, as_attachment=True)

    except Exception as e:
        flash(f"Une erreur est survenue lors de la sauvegarde : {e}", 'danger')
        return redirect(url_for('list_users'))  # Ou une autre page admin


# Dans app/routes.py, par exemple après la route 'details_demande'

# Dans app/routes.py

from datetime import date  # Assurez-vous que 'date' est importé depuis 'datetime' en haut du fichier


@app.route('/demande/<int:demande_id>/imprimer')
@login_required
def imprimer_demande(demande_id):
    demande = Demande.query.get_or_404(demande_id)

    # Sécurité
    if current_user.role.name == 'Chef d\'établissement' and demande.etablissement_id != current_user.etablissement_id:
        flash("Accès non autorisé.", 'danger')
        return redirect(url_for('mes_demandes'))

    # --- LIGNE À AJOUTER ---
    date_impression = date.today()

    return render_template('demandes/imprimer_demande.html',
                           demande=demande,
                           date_impression=date_impression)  # On passe la date au template


# Dans app/routes.py, à la fin de la section admin

@app.route('/admin/logs')
@login_required
@admin_required

def view_logs():
    """
    Affiche le journal de toutes les activités du système.
    """
    # On utilise la pagination pour ne pas afficher des milliers de lignes d'un coup
    # On affiche la page demandée (par défaut 1), avec 25 logs par page
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=25)

    return render_template('admin/logs.html', logs=logs, title="Journal d'Activité")