import sys

from celery_app import celery_app

worker = celery_app.worker_main(['worker',
                                 '--loglevel=info',
                                 '--concurrency=4',
                                 '--events',
                                 '--pool=prefork',
                                 f"--hostname={str(sys.argv[1])}"])
worker.start()
