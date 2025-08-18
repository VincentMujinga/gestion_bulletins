from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional
from ..models import Role

class UserForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe (laisser vide pour ne pas changer)", validators=[Optional(), Length(min=6)])
    role = SelectField("Rôle", choices=[(r.value, r.value) for r in Role], validators=[DataRequired()])
    etablissement_id = IntegerField("ID Établissement (optionnel)", validators=[Optional()])
    submit = SubmitField("Enregistrer")
