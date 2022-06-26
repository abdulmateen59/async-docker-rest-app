from celery import chain
from celery import states
from celery.result import AsyncResult
from fastapi import Body
from fastapi import status
from fastapi.responses import Response
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger

from celery_app import celery_app

router = InferringRouter(tags=['docker'], prefix='/api/v2/docker')


@router.post('/build/{image_name}/{version}',
             status_code=status.HTTP_202_ACCEPTED)
async def dockerfile_build_interface(image_name: str,
                                     version: str = 'latest',
                                     push: bool = False,
                                     file: str = Body(..., media_type='text/plain')):
    """
    Builds a docker image from a dockerfile.

    :param image_name: Docker image name.
    :param version: Docker image version (default: latest).
    :param push: Whether to push the image to the container registry (default: False).
    :param file: Dockerfile content.

    :return: JSON Response
    """

    tag = f"{version}-{image_name}"
    try:
        if push:
            logger.info(f"Build and publish new docker image {tag}")
            task = chain(celery_app.signature('celery_app.tasks.docker_image_builder',
                                              kwargs={'dockerfile': file, 'tag': tag},
                                              immutable=True),
                         celery_app.signature('celery_app.tasks.push_image',
                                              kwargs={'tag': tag},
                                              immutable=True)
                         ).apply_async(retry=True)

            return {'task_id': [task.id],
                    'status': 'Queued'}

        logger.info(f"Building new docker image {tag}")
        task = celery_app.signature('celery_app.tasks.docker_image_builder',
                                    kwargs={'dockerfile': file, 'tag': tag}).apply_async(retry=True)

        return {'task_id': [task.id],
                'status': 'Queued'}

    except Exception as e:
        logger.error(e)
        return Response(e, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@router.get('/task/{task_id}')
async def task_status(task_id: str):
    """
    Query task status.

    :param task_id: Task ID.

    :return: JSON Response
    """

    task = AsyncResult(task_id)
    logger.info(f"Task {task_id} status: {task.status}")
    if task.state == states.PENDING:
        response = {
            'id': [task.id],
            'state': task.state,
            'status': 'Pending...',
        }
    elif task.state != states.FAILURE:
        response = {
            'id': [task.id],
            'state': task.state,
            'status': task.info.get('status'),
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': [task.state],
            'status': str(task.info),  # Raised Exception
        }

    return response
