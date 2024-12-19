from locust import HttpUser, task, between

class LoadTestUser(HttpUser):
    wait_time = between(1, 5)  # Interval between requests (in seconds)

    @task
    def load_login(self):
        """Load testing the login page."""
        self.client.post("/", data={"username": "user", "password": "password"})

    @task
    def load_catalog(self):
        """Load testing the catalog page."""
        self.client.get("/catalog")

    @task
    def load_order(self):
        """Load testing the order placement."""
        self.client.post(
            "/order",
            data={"product_id": 1, "customer_email": "test@example.com"},
        )

    @task
    def load_logout(self):
        """Load testing the logout functionality."""
        self.client.get("/logout")
