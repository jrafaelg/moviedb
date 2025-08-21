from moviedb import create_app


def run():
    # criando o app com o arquivo das configs
    app = create_app("config.dev.json")

    # rodando com as configs do json
    app.run(host=app.config['APP_HOST'],
            port=app.config['APP_PORT'])

if __name__ == '__main__':
    run()