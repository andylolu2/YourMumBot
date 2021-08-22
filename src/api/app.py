import types
from fastapi import FastAPI, Request

from api.requestvars import request_global
from api import routes


def create_app() -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def init_requestvars(request: Request, call_next):
        initial_g = types.SimpleNamespace()
        initial_g.client_ip = request.client.host
        request_global.set(initial_g)
        response = await call_next(request)
        return response

    app.include_router(routes.router)
    return app
