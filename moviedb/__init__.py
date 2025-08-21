import json
import os

from flask import Flask


def create_app(config_filename: str = "config.dev.json") -> Flask:

    # instanciando o flask
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates',
                instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        app.config.from_file(config_filename, load=json.load)
        app.logger.debug('Config loaded')
    except FileNotFoundError:
        app.logger.error("Config file not found")
        exit(1)

    return app