# ==============================================================================
# Contenu COMPLET pour le fichier app/forms.py
# Étape : Ajout des fonctionnalités du Coordonnateur
# ==============================================================================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, InputRequired
from app.models import Role, Etablissement

class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

class AddUserForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=4, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Adresse email invalide.")])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')])
    role = SelectField('Rôle', coerce=int, validators=[DataRequired()])
    etablissement = SelectField('Établissement (si Chef d\'établissement)', coerce=int, validators=[Optional()])
    submit = SubmitField("Créer l'utilisateur")
    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(r.id, r.name) for r in Role.query.order_by('name').all()]
        self.etablissement.choices = [(0, '--- Aucun ---')] + [(e.id, e.nom) for e in Etablissement.query.order_by('nom').all()]

class EditUserForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=4, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Adresse email invalide.")])
    role = SelectField('Rôle', coerce=int, validators=[DataRequired()])
    etablissement = SelectField('Établissement (si Chef d\'établissement)', coerce=int, validators=[Optional()])
    password = PasswordField('Nouveau mot de passe (laisser vide pour ne pas changer)', validators=[Optional(), Length(min=6)])
    submit = SubmitField("Mettre à jour")
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(r.id, r.name) for r in Role.query.order_by('name').all()]
        self.etablissement.choices = [(0, '--- Aucun ---')] + [(e.id, e.nom) for e in Etablissement.query.order_by('nom').all()]

class EtablissementForm(FlaskForm):
    nom = StringField("Nom de l'établissement", validators=[DataRequired(), Length(max=200)])
    ville = StringField('Ville', validators=[Optional(), Length(max=100)])
    cecop = StringField('N° CECOP', validators=[Optional(), Length(max=50)])
    submit = SubmitField("Enregistrer")

class LigneDemandeForm(FlaskForm):
    class Meta:
        csrf = False
    type_ecole = StringField('Type', validators=[InputRequired()])
    niveau = StringField('Niveau/Classe', validators=[InputRequired()])
    option = StringField('Option')
    quantite = IntegerField('Quantité', validators=[InputRequired()], default=0)

class DemandeForm(FlaskForm):
    annee_scolaire = StringField('Année Scolaire (ex: 2024-2025)', validators=[InputRequired()])
    lignes = FieldList(FormField(LigneDemandeForm), min_entries=1)
    submit = SubmitField('Soumettre la Demande')

# --- NOUVEAU FORMULAIRE POUR LE COORDONNATEUR ---
class RejectionForm(FlaskForm):
    """
    Formulaire simple pour qu'un validateur puisse motiver sa décision de rejet.
    """
    motif_rejet = TextAreaField("Motif du rejet", validators=[DataRequired(), Length(min=10, message="Le motif doit contenir au moins 10 caractères.")])
    submit = SubmitField("Confirmer le Rejet")