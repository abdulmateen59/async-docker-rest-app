from server import FastAPIServer
from app import make_app
from settings import Settings


if __name__ == '__main__':
    fastapi_server = FastAPIServer()
    app_settings = Settings()
    app = make_app(app_settings)
    fastapi_server.start_server(app)
