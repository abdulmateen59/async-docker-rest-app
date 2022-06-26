from pydantic import BaseSettings


class Settings(BaseSettings):
    celery_broker_url: str = 'amqp://user:pwd@0.0.0.0:5672/'
    celery_result_backend: str = 'redis://0.0.0.0:6379/1'
    docker_registry_url: str = 'ghcr.io/abdulmateen59/async-docker-rest-app'
    # celery_broker_url: str
    # celery_result_backend: str
    # docker_registry_url: str = ''
    docker_registry_username: str = ''
    docker_registry_password: str = ''
