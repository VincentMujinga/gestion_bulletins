from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class CommandeForm(FlaskForm):
    niveau = StringField("Niveau", validators=[DataRequired(), Length(max=50)])
    option = StringField("Option", validators=[Length(max=50)])
    annee_scolaire = StringField("Année scolaire", validators=[DataRequired(), Length(max=20)])
    quantite = IntegerField("Quantité", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Soumettre la commande")

class ValidationForm(FlaskForm):
    motif_rejet = TextAreaField("Motif du rejet", validators=[Length(max=500)])
    submit_valider = SubmitField("Valider")
    submit_rejeter = SubmitField("Rejeter")
