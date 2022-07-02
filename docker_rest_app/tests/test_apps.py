import requests
from unittest import TestCase
from pathlib import Path
import subprocess
import time


class TestApp(TestCase):

    dockerfile: str = b"From alpine:latest \n RUN apk add --no-cache curl"
    image_name: str = 'test_image'
    tag: str = '0.0.1'
    docker_url: str = 'http://localhost:8080/api/v2/docker/build'
    task_url: str = 'http://localhost:8080/api/v2/docker/task'

    @staticmethod
    def _start_container() -> None:
        command = ['docker-compose',
                   '-f',
                   str(Path(__file__).parents[2] / 'docker-compose.yaml'),
                   'up',
                   '-d']
        p = subprocess.Popen(command)
        p.wait()

    @staticmethod
    def _stop_containers() -> None:
        command = ['docker-compose',
                   '-f',
                   str(Path(__file__).parents[2] / 'docker-compose.yaml'),
                   'down']
        p = subprocess.Popen(command)
        p.wait()

    @classmethod
    def setUpClass(cls) -> None:
        cls._start_container()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._stop_containers()

    def _send_docker_build_request(self, dockerfile: str) -> str:
        headers = {'Content-type': 'text'}
        response = requests.post(f'{self.docker_url}/{self.image_name}/{self.tag}',
                                 headers=headers,
                                 data=dockerfile)
        return response.json()['task_id']

    def test_task_submit(self) -> None:
        headers = {'Content-type': 'text'}
        response = requests.post(f'{self.docker_url}/{self.image_name}/{self.tag}',
                                 headers=headers,
                                 data=self.dockerfile)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['status'], 'Queued')

    def test_task_completion(self) -> None:
        task_id = self._send_docker_build_request(dockerfile=self.dockerfile)
        time.sleep(15)
        response = requests.get(f'{self.task_url}/{str(*task_id)}')
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['state'], 'SUCCESS')

    def test_task_failure(self) -> None:
        task_id = self._send_docker_build_request(dockerfile=f'@@@@++{self.dockerfile}``++')
        time.sleep(25)
        response = requests.get(f'{self.task_url}/{str(*task_id)}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['state'][0], 'FAILURE')

    def test_task_started_or_pending(self) -> None:
        task_id = self._send_docker_build_request(dockerfile=self.dockerfile)
        response = requests.get(f'{self.task_url}/{str(*task_id)}')
        time.sleep(1)
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json()['state'], ['STARTED', 'PENDING'])
