import json
import logging
import os

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

    app.logger.debug("registrando módulos")
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    import moviedb.models
    # login_manager.init_app(app)


    app.logger.debug("registrando blueprints")
    from moviedb.blueprints.root import bp as root_bp
    app.register_blueprint(root_bp)
    from moviedb.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    app.logger.debug("definindo processadores de contexto")
    @app.context_processor
    def inject_globals():
        return dict(app_config=app.config)

    app.logger.info("aplicação criada")

    return app