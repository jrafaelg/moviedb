from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, request, url_for, render_template, current_app
from flask_login import current_user, login_required, login_user, logout_user, user_unauthorized

from infra.tokens import create_jwt_token, verify_jwt_token
from moviedb.forms.auth import RegistrationForm, LoginForm
from moviedb import db
from moviedb.models.autenticacao import User

bp = Blueprint(name='auth',
               import_name=__name__,
               url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Exibe o formulário de registro de usuário e processa o cadastro.

    - Usuários já autenticados não podem acessar esta rota.
    - Se o formulário for enviado e validado, cria um novo usuário,
      salva no banco de dados, envia um email de confirmação e
      redireciona para a página inicial.
    - O usuário deve confirmar o email antes de conseguir logar.
    - Caso contrário, renderiza o template de registro.

    Returns:
        Response: Redireciona ou renderiza o template de registro.
    """
    if current_user.is_authenticated:
        flash("acesso não autorizado para usuários logados", category="warning")
        return redirect(request.referrer if request.referrer else url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():

        usuario = User()
        usuario.nome = form.nome.data
        usuario.email = form.email.data
        usuario.password = form.password.data
        usuario.ativo = False

        db.session.add(usuario)
        # Realiza o flush para garantir que o usuário tenha um ID gerado antes do commit.
        db.session.flush()
        # Atualiza o objeto usuário com os dados mais recentes do banco de dados.
        db.session.refresh(usuario)
        token = create_jwt_token(action='validate_email',
                                 sub=usuario.email)
        current_app.logger.debug(f"token de validação de email: {token}")
        body = render_template('auth/email_confirmation.jinja2',
                               nome=usuario.nome,
                               url=url_for('auth.valida_email', token=token))
        usuario.send_email(subject='Confirme seu email', body=body)
        db.session.commit()
        flash("Registrado com sucesso! Confira seu email antes de logar", category="success")
        return redirect(url_for('root.index'))


    return render_template("auth/register.jinja2",
                           title="cadastrar novo usuario",
                           form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Exibe o formulário de login e processa a autenticação do usuário.

    - Usuários já autenticados não podem acessar esta rota.
    - Se o formulário for enviado e validado, verifica as credenciais do usuário.
    - Se o usuário existir, estiver ativo e a senha estiver correta, realiza o login.
    - Redireciona para a página desejada ou para a página inicial.
    - Caso contrário, exibe mensagens de erro e permanece na página de login.

    Returns:
        Response: Redireciona ou renderiza o template de login.
    """
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
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('root.index')
        return next_page

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

@bp.route('/valida_email/<token>')
def valida_email(token):
    """
    Valida o email do usuário a partir de um token JWT.

    - Usuários autenticados não podem acessar esta rota.
    - O token é verificado e deve conter as claims 'sub' (email) e 'action' igual a
    'validate_email'.
    - Se o usuário existir, estiver inativo e o token for válido, ativa o usuário e exibe
    mensagem de sucesso.
    - Em caso de token inválido ou usuário já ativo, exibe mensagem de erro.

    Args:
        token (str): Token JWT enviado na URL para validação do email.

    Returns:
        Response: Redireciona para a página de login ou inicial, conforme o caso.
    """
    if current_user.is_authenticated:
        flash("acesso não autorizado para usuários logados", category="warning")
        return redirect(request.referrer if request.referrer else url_for('root.index'))

    claims = verify_jwt_token(token)
    current_app.logger.debug(f"claims: {claims}")
    if not(claims.get('valid', False) and {'sub', 'action'}.issubset(claims)):
        flash("Token incorreto", category="warning")
        return redirect(url_for('root.index'))

    current_app.logger.debug(f"claims.get('sub'): {claims.get('sub')}")
    usuario = User.get_by_email(claims.get('sub'))
    current_app.logger.debug(f"usuario: {usuario}")
    if (usuario is not None and
            not usuario.ativo and
            claims.get('action') == 'validate_email'):
        usuario.ativo = True
        flash(f"Email {usuario.email} validado!", category='success')
        db.session.commit()
        return redirect(url_for('auth.login'))

    flash("token invalido", category="warning")
    return redirect(url_for('auth.login'))

