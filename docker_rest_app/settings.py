from pydantic import BaseSettings


class Settings(BaseSettings):
    celery_broker_url: str
    celery_result_backend: str
    docker_registry_url: str = ''
    docker_registry_username: str = ''
    docker_registry_password: str = ''
