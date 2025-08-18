from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Commande, CommandeStatut, Etablissement, Role
from ..utils import roles_required
from .forms import CommandeForm, ValidationForm

orders_bp = Blueprint("orders", __name__, template_folder="../templates/orders")

@orders_bp.route("/")
@login_required
def list_my():
    if current_user.role == Role.CHEF_ETABLISSEMENT:
        commandes = Commande.query.filter_by(etablissement_id=current_user.etablissement_id).order_by(Commande.created_at.desc()).all()
    else:
        commandes = Commande.query.order_by(Commande.created_at.desc()).all()
    return render_template("orders/list.html", commandes=commandes)

@orders_bp.route("/create", methods=["GET","POST"])
@login_required
@roles_required(Role.CHEF_ETABLISSEMENT)
def create():
    form = CommandeForm()
    if form.validate_on_submit():
        commande = Commande(
            etablissement_id=current_user.etablissement_id,
            niveau=form.niveau.data.strip(),
            option=form.option.data.strip() if form.option.data else None,
            annee_scolaire=form.annee_scolaire.data.strip(),
            quantite=form.quantite.data,
            statut=CommandeStatut.EN_ATTENTE
        )
        db.session.add(commande)
        db.session.commit()
        flash("Commande soumise avec succès.", "success")
        return redirect(url_for("orders.list_my"))
    return render_template("orders/create.html", form=form)

@orders_bp.route("/valider/<int:commande_id>", methods=["GET","POST"])
@login_required
@roles_required(Role.COORDONNATEUR)
def valider(commande_id):
    commande = Commande.query.get_or_404(commande_id)
    form = ValidationForm()
    if form.validate_on_submit():
        if form.submit_valider.data:
            commande.statut = CommandeStatut.VALIDEE
            commande.coordonnateur_id = current_user.id
            db.session.commit()
            flash("Commande validée et transmise au Sous-Proved.", "success")
        elif form.submit_rejeter.data:
            commande.statut = CommandeStatut.REJETEE
            commande.motif_rejet = form.motif_rejet.data.strip() or "Non spécifié"
            commande.coordonnateur_id = current_user.id
            db.session.commit()
            flash("Commande rejetée.", "warning")
        return redirect(url_for("orders.list_my"))
    return render_template("orders/valider.html", commande=commande, form=form)

@orders_bp.route("/approuver/<int:commande_id>", methods=["GET","POST"])
@login_required
@roles_required(Role.SOUS_PROVED)
def approuver(commande_id):
    commande = Commande.query.get_or_404(commande_id)
    form = ValidationForm()
    if form.validate_on_submit():
        if form.submit_valider.data:
            commande.statut = CommandeStatut.APPROUVEE
            commande.sous_proved_id = current_user.id
            db.session.commit()
            flash("Commande approuvée et transmise au Proved.", "success")
        elif form.submit_rejeter.data:
            commande.statut = CommandeStatut.REJETEE
            commande.motif_rejet = form.motif_rejet.data.strip() or "Non spécifié"
            commande.sous_proved_id = current_user.id
            db.session.commit()
            flash("Commande rejetée.", "warning")
        return redirect(url_for("orders.list_my"))
    return render_template("orders/valider.html", commande=commande, form=form)

@orders_bp.route("/distribuer/<int:commande_id>", methods=["POST","GET"])
@login_required
@roles_required(Role.PROVED)
def distribuer(commande_id):
    from ..models import BulletinStock
    commande = Commande.query.get_or_404(commande_id)
    # Simple allocation logic (no partials for now)
    stock = BulletinStock.query.filter_by(niveau=commande.niveau, option=commande.option).first()
    if request.method == "POST":
        if not stock or stock.quantite_disponible <= 0:
            flash("Stock insuffisant pour cette commande.", "danger")
            return redirect(url_for("orders.list_my"))
        q = min(stock.quantite_disponible, commande.quantite)
        stock.quantite_disponible -= q
        if q == commande.quantite:
            commande.statut = CommandeStatut.DISTRIBUEE
        else:
            commande.statut = CommandeStatut.PARTIELLE
        from flask_login import current_user
        commande.proved_id = current_user.id
        db.session.commit()
        flash("Distribution effectuée.", "success")
        return redirect(url_for("orders.list_my"))
    return render_template("orders/distribuer.html", commande=commande, stock=stock)
