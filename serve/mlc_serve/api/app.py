from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ollm.errors import TokenValidationError

from ..engine import AsyncEngineConnector
from .handler import router


def create_app(async_engine_connector: AsyncEngineConnector) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await async_engine_connector.start()
        app.state.async_engine_connector = async_engine_connector
        yield
        await async_engine_connector.stop()

    app = FastAPI(lifespan=lifespan)

    @app.exception_handler(TokenValidationError)
    async def token_validation_error_handler(_request: Request, exc: TokenValidationError) -> JSONResponse:
        return exc.to_response()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app