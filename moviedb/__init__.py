import json
import logging
import os
import sys


from flask import Flask

from moviedb.infra import app_logging
from moviedb.infra.modulos import bootstrap, db, migrate, login_manager


def create_app(config_filename: str = "config.dev.json") -> Flask:

    # instanciando o flask
    app = Flask(__name__,
                static_folder='static',
                template_folder="templates",
                instance_relative_config=True
                )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # chamando o log
    app_logging.configure_logging(logging.DEBUG)

    app.logger.debug("configurando a aplicação a partir do arquivo '%s'" % config_filename)

    try:
        app.config.from_file(config_filename, load=json.load)
        app.logger.debug('Config loaded')
    except FileNotFoundError:
        app.logger.error("Config file not found")
        exit(1)

    if "SQLALCHEMY_DATABASE_URI" not in app.config:
        app.logger.fatal("No database URI")
        sys.exit(1)

    if "APP_HOST" not in app.config:
        app.logger.warning("No host defined")
        app.config["APP_HOST"] = "0.0.0.0"

    if "APP_PORT" not in app.config:
        app.logger.warning("No port defined")
        app.config["APP_PORT"] = 5000

    if "SECRET_KEY" not in app.config or app.config.get("SECRET_KEY") is None:
        app.logger.warning("No secret key defined")
        app.config["SECRET_KEY"] = os.urandom(32).hex()
        app.logger.warning("Secret key generated: '%s'" % app.config["SECRET_KEY"])
        app.logger.warning("Para não invalidar os logins persistentes e os JWT "
                           "gerados efetuados nesta instância da aplicação, "
                           "adicione a chave acima ao arquivo de configuração")


    app.logger.debug("registrando módulos")
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    login_manager.init_app(app)

    app.logger.debug("definindo as mensagens padrão")
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Para acessar este recurso, você precisa estar logado!"
    login_manager.login_message_category = 'info'


    app.logger.debug("registrando blueprints")
    from moviedb.blueprints.root import bp as root_bp
    app.register_blueprint(root_bp)
    from moviedb.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    app.logger.debug("definindo processadores de contexto")
    @app.context_processor
    def inject_globals():
        return dict(app_config=app.config)

    app.logger.debug("definindo o callback de login")

    # https://flask-login.readthedocs.io/en/latest/#alternative-tokens
    @login_manager.user_loader
    def user_load(user_id):
        from moviedb.models.autenticacao import User
        import uuid

        id_usuario, final_da_senha = user_id.split('|', 1)
        try:
            auth_id = uuid.UUID(id_usuario)
        except ValueError:
            return None
        usuario = User.get_by_id(auth_id)
        return usuario if usuario and usuario.password.endswith(final_da_senha) else None

    app.logger.info("aplicação criada")

    return app