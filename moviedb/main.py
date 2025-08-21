from moviedb import create_app

# repositório Lobato
# https://github.com/TINF-IFSP-RioPreto/2025-DWII-MovieDB

def run():
    # criando o app com o arquivo das configs
    app = create_app("config.dev.json")

    # rodando com as configs do json
    app.run(host=app.config['APP_HOST'],
            port=app.config['APP_PORT'])

if __name__ == '__main__':
    run()