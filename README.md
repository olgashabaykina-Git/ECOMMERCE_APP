
E-Commerce App
The E-Commerce App is a Flask-based web application designed for demonstrating user authentication, product catalog management, order placement, and integration with email notifications. The application is built with an emphasis on robust testing, monitoring, and deployment using modern tools and frameworks.

Features
User Authentication: Secure login and logout functionality.
Product Catalog: Displays a list of products with prices.
Order Placement: Allows users to place orders after entering their email.
Email Notifications: Sends order confirmation emails using the SendGrid API.
Monitoring: Integrated with Prometheus and Grafana to monitor application metrics.
Testing:
Unit tests for core components.
Integration tests to verify module interaction.
End-to-end tests using Selenium for user interaction flows.
Load testing with Locust to measure performance under stress.
GitHub Actions CI Pipeline: Automates the testing and reporting workflow.
Installation Instructions (Mac)
Prerequisites
Python 3.11
Virtual environment (venv)
Docker (for monitoring stack)
Google Chrome
ChromeDriver
Steps to Set Up
Clone the Repository:

git clone <repository-url>
cd ecommerce_app
Set Up Python: Ensure Python 3.11 is installed. If not, install it using Homebrew:

brew install python
python3 --version
Create a Virtual Environment:

python3 -m venv venv
source venv/bin/activate
Install Dependencies:

pip install --upgrade pip
pip install -r requirements.txt
Set Up Environment Variables: Create a .env file with the following content:

FLASK_SECRET_KEY=your_secret_key
SENDGRID_API_KEY=your_sendgrid_api_key
Run the Application:

python app.py
Access the Application: Navigate to http://localhost:5001 in your web browser.

##Testing Instructions ###Types of Tests

Unit Tests: Run unit tests to validate core functionality:

pytest tests/test_unit.py
integration Tests: Ensure modules interact as expected:

pytest tests/test_integration.py
End-to-End Tests: Verify user interactions from start to finish:

python run_e2e_tests.py
Load Tests: Simulate multiple users accessing the application:

locust
Visit http://localhost:8089 to manage and monitor load tests.

GitHub Actions CI Pipeline
The CI pipeline is defined in .github/workflows/test.yml and automates the testing process. It includes the following steps:
Checkout repository.
Install Google Chrome
Set up Python environment
Clean Python cache and install dependencies
Start the application server
Run Tests:Executes unit tests, integration tests, and end-to-end tests.
Upload HTML reports
Trigger Conditions On every push to the main branch,On pull requests targeting the main branch.
Setting Secrets: Ensure that the SENDGRID_API_KEY is added as a secret in the GitHub repository settings.
Monitoring with Prometheus and Grafana
The application integrates with Prometheus and Grafana for real-time monitoring of application metrics.
Steps to Start Monitoring
Start Docker Services: Run the following command to start Prometheus, Grafana, and Pushgateway:
docker-compose up
Access Monitoring Tools:
Prometheus: http://localhost:9090
Grafana: http://localhost:3000 (Default credentials: admin/admin)
Prometheus Configuration: Prometheus is configured to scrape metrics from the application at the /metrics endpoint.
##Directory Structure

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
