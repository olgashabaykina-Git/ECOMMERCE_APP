# E-Commerce Application

The E-Commerce App is a Flask-based web application designed for demonstrating user authentication, product catalog management, order placement, and integration with email notifications. The application is built with an emphasis on robust testing, monitoring, and deployment using modern tools and frameworks.

## Features

- **User Authentication**: Secure login and logout functionality.
- **Product Catalog**: Displays a list of products with prices.
- **Order Placement**: Allows users to place orders after entering their email.
- **Email Notifications**: Sends order confirmation emails using the SendGrid API.
- **Monitoring**: Integrated with Prometheus and Grafana to monitor application metrics.
- **Testing**:
  - Unit tests for core components.
  - Integration tests to verify module interaction.
  - End-to-end tests using Selenium for user interaction flows.
  - Load testing with Locust to measure performance under stress.
- **GitHub Actions CI Pipeline**: Automates the testing and reporting workflow.

## Installation Instructions (Mac)

### Prerequisites

- Python 3.11
- Virtual environment (venv)
- Docker (for monitoring stack)
- Google Chrome
- ChromeDriver

### Steps to Set Up

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/olgashabaykina-Git/ECOMMERCE_APP.git
   cd ecommerce_app
   ```

2. **Set Up Python**:

   Ensure Python 3.11 is installed. If not, install it using Homebrew:

   ```bash
   brew install python
   python3 --version
   ```

3. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**:

   Create a `.env` file with the following content:

   ```env
   FLASK_SECRET_KEY=your_secret_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```

6. **Run the Application**:

   ```bash
   python app.py
   ```

7. **Access the Application**:

   Navigate to http://127.0.0.1:5001 in your web browser.

8. To log in using these details: Usersname = user
Password = password



## Testing Instructions

### Types of Tests

- **Unit Tests**: Run unit tests to validate core functionality:
  
  ```bash
  pytest tests/test_unit.py
  ```

- **Integration Tests**: Ensure modules interact as expected:
  
  ```bash
  pytest tests/test_integration.py
  ```

- **End-to-End Tests**: Verify user interactions from start to finish:
  
  ```bash
  python run_e2e_tests.py
  ```

- **Load Tests**: Simulate multiple users accessing the application:
  
  ```bash
  locust
  ```

  Visit [http://localhost:8089](http://localhost:8089) to manage and monitor load tests.

## GitHub Actions CI Pipeline

The CI pipeline is defined in `.github/workflows/test.yml` and automates the testing process. It includes the following steps:

1. Checkout repository.
2. Install Google Chrome.
3. Set up Python environment.
4. Clean Python cache and install dependencies.
5. Start the application server.
6. Run Tests: Executes unit tests, integration tests, and end-to-end tests.
7. Upload HTML reports.

### Trigger Conditions

- On every push to the `main` branch.
- On pull requests targeting the `main` branch.

### Setting Secrets

Ensure that the `SENDGRID_API_KEY` is added as a secret in the GitHub repository settings.

## Monitoring with Prometheus and Grafana

The application integrates with Prometheus and Grafana for real-time monitoring of application metrics.

### Steps to Start Monitoring

1. **Start Docker Services**:

   Run the following command to start Prometheus, Grafana, and Pushgateway:

   ```bash
   docker-compose up
   ```

2. **Access Monitoring Tools**:

   - **Prometheus**: [http://localhost:9090](http://localhost:9090)
   - **Grafana**: [http://localhost:3000](http://localhost:3000) (Default credentials: admin/admin)

3. **Prometheus Configuration**:

   Prometheus is configured to scrape metrics from the application at the `/metrics` endpoint.

## Directory Structure

```
ecommerce_app/
├── app.py                     # Main application code
├── docker-compose.yml         # Configuration for Docker services
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation
├── tests/                     # Test scripts
│   ├── test_unit.py           # Unit tests
│   ├── test_integration.py    # Integration tests
│   ├── test_e2e.py            # End-to-End tests
│   ├── load_test.py           # Load tests
│   ├── conftest.py            # Pytest fixtures and setup
├── static/                    # Static files (CSS)
├── templates/                 # HTML templates for the app
│   ├── catalog.html
│   ├── login.html
├── .github/workflows/         # GitHub Actions workflows
│   └── test.yml               # CI pipeline configuration
├── prometheus.yml             # Prometheus configuration
├── run_e2e_tests.py           # End-to-End test runner
```

