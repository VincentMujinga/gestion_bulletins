from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ..extensions import db
from ..models import BulletinStock, Role
from ..utils import roles_required

stock_bp = Blueprint("stock", __name__, template_folder="../templates/stock")

@stock_bp.route("/")
@login_required
@roles_required(Role.PROVED)
def index():
    stocks = BulletinStock.query.order_by(BulletinStock.niveau.asc()).all()
    return render_template("stock/stock.html", stocks=stocks)

@stock_bp.route("/add", methods=["POST"])
@login_required
@roles_required(Role.PROVED)
def add():
    niveau = request.form.get("niveau", "").strip()
    option = request.form.get("option", "").strip() or None
    quantite = int(request.form.get("quantite", 0))
    if not niveau or quantite <= 0:
        flash("Données invalides.", "danger")
        return redirect(url_for("stock.index"))
    from ..models import BulletinStock
    s = BulletinStock.query.filter_by(niveau=niveau, option=option).first()
    if s:
        s.quantite_disponible += quantite
    else:
        s = BulletinStock(niveau=niveau, option=option, quantite_disponible=quantite)
        db.session.add(s)
    db.session.commit()
    flash("Stock mis à jour.", "success")
    return redirect(url_for("stock.index"))
