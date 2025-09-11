from flask import Blueprint, flash, redirect, request, url_for, render_template
from flask_login import current_user

from forms.auth import RegistrationForm
from moviedb import db
from moviedb.models.autenticacao import User

bp = Blueprint(name='auth',
               import_name=__name__,
               url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     flash("acesso não autorizado para usuários logados", category="warning")
    #     return redirect(request.referrer if request.referrer else url_for("index"))

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

