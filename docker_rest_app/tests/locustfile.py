from locust import HttpUser
from locust import between
from locust import task


class AppUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_index(self):
        self.client.get("/health")

    @task
    def get_index(self):
        self.client.post("/api/v2/docker/build/test_image/0.0.1?push=False",
                         headers={"Content-type": "text"},
                         data=b'From alpine:latest \n RUN apk add --no-cache curl')
