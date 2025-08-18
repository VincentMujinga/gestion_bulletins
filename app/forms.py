# Contenu FINAL et COMPLET pour app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models import Role

# ... (gardez votre LoginForm) ...
class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

# Ce formulaire est pour l'admin
class AddUserForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=4, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')])
    # Le champ pour sélectionner un rôle
    role = SelectField('Rôle', coerce=int, validators=[DataRequired()])
    submit = SubmitField("Créer l'utilisateur")

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        # Cette ligne remplit la liste déroulante avec les rôles de la base de données
        self.role.choices = [(r.id, r.name) for r in Role.query.order_by('name').all()]