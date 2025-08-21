# ==============================================================================
# Contenu FINAL, VÉRIFIÉ ET CORRECT pour le fichier app/models.py
# ==============================================================================

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')


class Etablissement(db.Model):
    __tablename__ = 'etablissements'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False, unique=True)
    ville = db.Column(db.String(100))
    cecop = db.Column(db.String(50), nullable=True)
    utilisateurs = db.relationship('User', backref='etablissement', lazy='dynamic')
    demandes = db.relationship('Demande', backref='etablissement', lazy='dynamic')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=True)

    # Les relations 'backref' des autres modèles créeront automatiquement
    # les attributs 'notifications', 'logs', et 'demandes_traitees' sur cet objet User.

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Demande(db.Model):
    __tablename__ = 'demandes'
    id = db.Column(db.Integer, primary_key=True)
    annee_scolaire = db.Column(db.String(20), nullable=False)
    date_demande = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='Soumise')
    etablissement_id = db.Column(db.Integer, db.ForeignKey('etablissements.id'), nullable=False)
    lignes = db.relationship('LigneDemande', backref='demande', lazy='dynamic', cascade="all, delete-orphan")

    # Champs pour la traçabilité
    processeur_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date_traitement = db.Column(db.DateTime, nullable=True)

    # Relation pour retrouver facilement l'utilisateur qui a traité la demande
    processeur = db.relationship('User', foreign_keys=[processeur_id])

    @property
    def total_quantite(self):
        return sum(ligne.quantite for ligne in self.lignes)


class LigneDemande(db.Model):
    __tablename__ = 'ligne_demandes'
    id = db.Column(db.Integer, primary_key=True)
    type_ecole = db.Column(db.String(50), nullable=False)
    niveau = db.Column(db.String(50), nullable=False)
    option = db.Column(db.String(100), nullable=True)
    quantite = db.Column(db.Integer, nullable=False, default=0)
    demande_id = db.Column(db.Integer, db.ForeignKey('demandes.id'), nullable=False)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Ligne CORRECTE :
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic', cascade="all, delete-orphan"))

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    action = db.Column(db.String(512), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Ligne CORRECTE :
    user = db.relationship('User', backref=db.backref('logs', lazy='dynamic', cascade="all, delete-orphan"))
    def __repr__(self):
        return f'<Log {self.action}>'