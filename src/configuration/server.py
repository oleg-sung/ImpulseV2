from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


class Server:
    __app: FastAPI

    def __init__(self, app: FastAPI) -> None:
        self.__app = app
        self.__register_middleware(app)
        self.__register_events(app)
        self.__register_routes(app)
        self.__register_static_path(app)

    def get_app(self) -> FastAPI:
        return self.__app

    @staticmethod
    def __register_events(_app: FastAPI) -> None: ...

    @staticmethod
    def __register_routes(_app: FastAPI) -> None:
        from src.configuration.routes import __routes__

        __routes__.register_routes(_app)

    @staticmethod
    def __register_middleware(app: FastAPI) -> None:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @staticmethod
    def __register_static_path(app: FastAPI) -> None:
        app.mount("/static", StaticFiles(directory="src/static"), name="static")
