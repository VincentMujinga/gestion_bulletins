# Contenu de app/admin/routes.py
from flask import render_template, flash, redirect, url_for
from app.admin import bp
from app.decorators import admin_required
from app.models import User, Role
from app.forms import AddUserForm
from app import db

@bp.route('/users')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users, title="Gestion des Utilisateurs")

@bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur ou l'email n'existe pas déjà
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Ce nom d\'utilisateur ou cet email est déjà utilisé.', 'danger')
            return redirect(url_for('admin.add_user'))

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role_id=form.role.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Le nouvel utilisateur a été créé avec succès.', 'success')
        return redirect(url_for('admin.list_users'))

    return render_template('admin/add_user.html', form=form, title="Ajouter un Utilisateur")# Contenu de app/admin/routes.py
from flask import render_template, flash, redirect, url_for
from app.admin import bp
from app.decorators import admin_required
from app.models import User, Role
from app.forms import AddUserForm
from app import db

@bp.route('/users')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users, title="Gestion des Utilisateurs")

@bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur ou l'email n'existe pas déjà
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Ce nom d\'utilisateur ou cet email est déjà utilisé.', 'danger')
            return redirect(url_for('admin.add_user'))

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role_id=form.role.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Le nouvel utilisateur a été créé avec succès.', 'success')
        return redirect(url_for('admin.list_users'))

    return render_template('admin/add_user.html', form=form, title="Ajouter un Utilisateur")