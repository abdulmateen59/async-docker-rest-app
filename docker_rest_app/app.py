from fastapi import FastAPI
from routers import docker_router
from settings import Settings


def make_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Async Docker Rest Application",
        description="",
        version="0.1.0",
    )
    app.state.settings = settings
    app.include_router(docker_router.router)

    @app.get("/health")
    def status_markdown() -> str:
        return "I'm doing good and hope the same :) "

    return app
