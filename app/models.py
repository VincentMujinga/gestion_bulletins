# ==============================================================================
# Contenu COMPLET et CORRECT pour le fichier app/models.py
# Étape : Ajout des modèles Etablissement et Demande
# ==============================================================================

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    """
    Modèle représentant les rôles des utilisateurs (Admin, Chef d'établissement, etc.).
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'


# Dans app/models.py

class Etablissement(db.Model):
    __tablename__ = 'etablissements'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False, unique=True)
    ville = db.Column(db.String(100))

    # ===== LIGNE À AJOUTER =====
    cecop = db.Column(db.String(50), nullable=True, unique=True)
    # ===========================

    utilisateurs = db.relationship('User', backref='etablissement', lazy='dynamic')
    demandes = db.relationship('Demande', backref='etablissement', lazy='dynamic')

    def __repr__(self):
        return f'<Etablissement {self.nom}>'
    def __repr__(self):
        return f'<Etablissement {self.nom}>'


class User(UserMixin, db.Model):
    """
    Modèle représentant un utilisateur du système.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Clé étrangère vers la table des rôles
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # MODIFICATION : Clé étrangère vers la table des établissements.
    # Un utilisateur peut être associé à un établissement (s'il est Chef d'établissement).
    # 'nullable=True' car un Admin ou un Proved n'est pas lié à une seule école.
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# Dans app/models.py
# ... (gardez les autres imports et modèles)

class Demande(db.Model):
    __tablename__ = 'demandes'
    id = db.Column(db.Integer, primary_key=True)
    annee_scolaire = db.Column(db.String(20), nullable=False)  # Ex: 2024-2025
    date_demande = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='Soumise')
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=False)

    # NOUVELLE RELATION : Une demande contient plusieurs lignes
    lignes = db.relationship('LigneDemande', backref='demande', lazy='dynamic', cascade="all, delete-orphan")

    # Propriété pour calculer le total dynamiquement
    @property
    def total_quantite(self):
        return sum(ligne.quantite for ligne in self.lignes)

    def __repr__(self):
        return f'<Demande {self.id} pour {self.etablissement.nom}>'


# NOUVEAU MODÈLE POUR LES LIGNES DE LA DEMANDE
class LigneDemande(db.Model):
    __tablename__ = 'ligne_demandes'
    id = db.Column(db.Integer, primary_key=True)
    type_ecole = db.Column(db.String(50), nullable=False)  # Maternelle, Primaire, Secondaire
    niveau = db.Column(db.String(50), nullable=False)
    option = db.Column(db.String(100), nullable=True)  # Optionnel, seulement pour le secondaire
    quantite = db.Column(db.Integer, nullable=False, default=0)

    # Clé étrangère vers la demande parente
    demande_id = db.Column(db.Integer, db.ForeignKey('demandes.id'), nullable=False)

    def __repr__(self):
        return f'<Ligne {self.id}: {self.quantite} pour {self.niveau}>'