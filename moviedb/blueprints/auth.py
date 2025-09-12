from flask import Blueprint, flash, redirect, request, url_for, render_template
from flask_login import current_user, login_required, login_user, logout_user

from moviedb.forms.auth import RegistrationForm, LoginForm
from moviedb import db
from moviedb.models.autenticacao import User

bp = Blueprint(name='auth',
               import_name=__name__,
               url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("acesso não autorizado para usuários logados", category="warning")
        return redirect(request.referrer if request.referrer else url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        usuario = User()
        usuario.nome = form.nome.data
        usuario.email = form.email.data
        usuario.password = form.password.data
        usuario.ativo = True

        db.session.add(usuario)
        db.session.commit()
        flash("Registrado com sucesso!", category="success")
        return redirect(url_for('root.index'))


    return render_template("auth/register.jinja2",
                           title="cadastrar novo usuario",
                           form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        flash("Você já está logado", category="info")
        return redirect(url_for('root.index'))

    form = LoginForm()

    if form.validate_on_submit():
        usuario = User.get_by_email(form.email.data)
        if usuario is None or not usuario.check_password(form.password.data):
            flash("Usuário ou senha invalidos!", category="warning")
            return redirect(url_for('auth.login'))
        if not usuario.is_active():
            flash("Usuário impedido de usar o sistema!", category="danger")
            return redirect(url_for('auth.login'))

        login_user(usuario, remember=form.remember_me.data)
        flash("Usuário logado!", category="success")
        return redirect(url_for('root.index'))

    return render_template("auth/login.jinja2",
                           title="Logar",
                           form=form)

@bp.route('/logout')
@login_required
def logout():
    """
    Realiza o logout do usuário autenticado.

    - Encerra a sessão do usuário.
    - Exibe uma mensagem de sucesso.
    - Redireciona para a página inicial.

    Returns:
        Response: Redireciona para a página inicial após logout.
    """
    logout_user()
    flash("Logout efetuado com sucesso!", category='success')
    return redirect(url_for('root.index'))