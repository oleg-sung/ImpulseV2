from fastapi import FastAPI

from .configuration.server import Server


def create_app(_=None) -> FastAPI:
    app = FastAPI(debug=True)
    return Server(app).get_app()
