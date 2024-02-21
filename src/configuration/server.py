from fastapi import FastAPI


class Server:
    __app: FastAPI

    def __init__(self, app: FastAPI) -> None:
        self.__app = app
        self.__register_events(app)
        self.__register_routes(app)

    def get_app(self) -> FastAPI:
        return self.__app

    @staticmethod
    def __register_events(_app: FastAPI) -> None: ...

    @staticmethod
    def __register_routes(_app: FastAPI) -> None:
        from src.configuration.routes import __routes__

        __routes__.register_routes(_app)
