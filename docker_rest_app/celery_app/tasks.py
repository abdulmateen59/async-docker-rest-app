import traceback
from io import BytesIO

import docker
from celery import states
from loguru import logger

from celery_app import celery_app
from celery_app import settings


@celery_app.task(bind=True)
def docker_image_builder(self,
                         dockerfile: str,
                         tag: str) -> dict[str, list[str] | str]:
    """
    Background task that builds and push docker image to the container registry .

    :param dockerfile: Content of the dockerfile.
    :param tag: Tag for the docker image.

    :return: None
    """

    tag: str = f"{settings.docker_registry_url}:{tag}"
    logger.info(f'Starting with {tag}...')
    try:
        dockerfile_b: BytesIO = BytesIO(dockerfile.encode('utf-8'))
        client = docker.from_env()
        _, logs = client.images.build(fileobj=dockerfile_b,
                                      tag=f'{tag}',
                                      pull=True,
                                      forcerm=True,
                                      nocache=True)
        result: list[str] = []
        for items in logs:
            result.extend(value for _, value in items.items())
        logger.info(f'{self.request.id} - {tag} - Built Successfully')
        return {'status': 'Built successfully!',
                'result': result,
                'tag': tag}

    except Exception as ex:
        logger.error(ex)
        self.update_state(state=states.FAILURE,
                          meta={'exc_type': type(ex).__name__,
                                'exc_message': traceback.format_exc().split('\n')})
        raise ex


@celery_app.task(bind=True)
def push_image(self,
               tag: str):
    """
    Background task that builds and push docker image to the container registry .

    :param dockerfile: Content of the dockerfile.
    :param tag: Tag for the docker image.

    :return: None
    """

    try:
        tag: str = f"{settings.docker_registry_url}:{tag}"
        client = docker.from_env()
        logger.info(f'Preparing {tag} docker image')

        registry_logs: str = client.api.push(tag, auth_config={'username': settings.docker_registry_username,
                                                               'password': settings.docker_registry_password})
        if 'error' in registry_logs:
            self.update_state(state=states.FAILURE,
                              meta={'exc_type': 'Docker Registry Error',
                                    'exc_message': registry_logs})
            raise ModuleNotFoundError(registry_logs)

        logger.info(f'{self.request.id} - {tag} - Pushed Successfully')
        return {'status': 'Pushed Successfully',
                'result': registry_logs}

    except Exception as ex:
        logger.error(ex)
        self.update_state(state=states.FAILURE,
                          meta={'exc_type': type(ex).__name__,
                                'exc_message': traceback.format_exc().split('\n')})
        raise ex


@celery_app.task
def send_email() -> dict[str, str]:
    """
    Background task that sends an email to the user.
    """

    logger.info('Sending email to user...')
    return {'status': 'Email sent'}
