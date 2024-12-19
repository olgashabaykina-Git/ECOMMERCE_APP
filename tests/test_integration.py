from prometheus_client import Gauge, push_to_gateway, REGISTRY
import unittest
from unittest.mock import patch
from app import app, users, products, orders, send_email, order_placed_notification
import logging
import sys
from app import app

import os
os.environ['COVERAGE_RUN'] = 'true'  

# Configure logging to both file and console
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# File handler to log to 'integration_test_app.log'
file_handler = logging.FileHandler("integration_test_app.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Console handler to log to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Job name for Prometheus Pushgateway
JOB_NAME = 'test_job'

# Define Gauges for Prometheus metrics
tests_total_gauge = Gauge('tests_total', 'Total number of tests run')
tests_passed_gauge = Gauge('tests_passed', 'Number of tests passed')
tests_failed_gauge = Gauge('tests_failed', 'Number of tests failed')

# Global variables to track test counts
test_count = 0
tests_passed_count = 0
tests_failed_count = 0

def push_metrics():
    """
    Pushing the collected metrics to the Prometheus Pushgateway.
    """
    global test_count, tests_passed_count, tests_failed_count
    # Update Gauges with the current counts
    tests_total_gauge.set(test_count)
    tests_passed_gauge.set(tests_passed_count)
    tests_failed_gauge.set(tests_failed_count)
    
    # Using print instead of logging to avoid issues with closed log handlers during shutdown
    print(f"Pushing metrics - Total: {test_count}, Passed: {tests_passed_count}, Failed: {tests_failed_count}")
    try:
        push_to_gateway('localhost:9091', job=JOB_NAME, registry=REGISTRY)
    except Exception as e:
        print(f"Failed to push metrics: {e}")

class CustomTestResult(unittest.TextTestResult):
    """
    Custom TestResult class to update Prometheus metrics based on test outcomes.
    """
    def startTest(self, test):
        global test_count
        super().startTest(test)
        test_count += 1
        print(f"Started test: {test} | tests_total: {test_count}")

    def addSuccess(self, test):
        global tests_passed_count
        super().addSuccess(test)
        tests_passed_count += 1
        print(f"Test passed: {test} | tests_passed: {tests_passed_count}")

    def addFailure(self, test, err):
        global tests_failed_count
        super().addFailure(test, err)
        tests_failed_count += 1
        print(f"Test failed: {test} - {err} | tests_failed: {tests_failed_count}")

    def addError(self, test, err):
        global tests_failed_count
        super().addError(test, err)
        tests_failed_count += 1
        print(f"Test error: {test} - {err} | tests_failed: {tests_failed_count}")

class CustomTestRunner(unittest.TextTestRunner):
    """
    Custom TestRunner class that uses the CustomTestResult and pushes metrics after tests run.
    """
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)
    
    def run(self, test):
        """
        Override the run method to push metrics after all tests have been executed.
        """
        result = super().run(test)
        push_metrics()
        return result

class TestApp(unittest.TestCase):
    def setUp(self):
        """Setting up the client for tests and clearing orders before each test."""
        logging.info("Setting up test client and clearing orders.")
        self.app = app.test_client()
        self.app.testing = True
        orders.clear() 

    def test_login_success(self):
        """Successful login test."""
        logging.info("Starting test: test_login_success")
        response = self.app.post('/', data={'username': 'user', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Redirect to /catalog
        with self.app.session_transaction() as sess:
            self.assertIn('user', sess)  # Checking for user session
        logging.info("Test login_success completed successfully.")

    def test_login_failure(self):
        """Bad Password Failed Login Test."""
        logging.info("Starting test: test_login_failure")
        response = self.app.post('/', data={'username': 'user', 'password': 'wrong'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid credentials. Please try again.', response.data)
        logging.info("Test login_failure completed with expected invalid credentials message.")

    def test_catalog_access_without_login(self):
        """Test catalog access without logging in."""
        logging.info("Starting test: test_catalog_access_without_login")
        response = self.app.get('/catalog')
        self.assertEqual(response.status_code, 302)  # Redirect to /
        self.assertIn('/', response.headers['Location'])
        logging.info("Unauthorized catalog access redirected as expected.")

    def test_order_without_login(self):
        """Test attempt to place an order without logging in."""
        logging.info("Starting test: test_order_without_login")
        response = self.app.post('/order', data={'product_id': 1, 'customer_email': 'test@example.com'})
        self.assertEqual(response.status_code, 302)  # Redirect to /
        self.assertIn('/', response.headers['Location'])
        logging.info("Order attempt without login redirected as expected.")

    @patch('app.send_email')
    def test_order_placed(self, mock_send_email):
        """There is a successful order placement and email sending."""
        logging.info("Starting test: test_order_placed")
        mock_send_email.return_value = (202, 'Email sent successfully')

        # User Login
        self.app.post('/', data={'username': 'user', 'password': 'password'})
        logging.info("User logged in for order placement.")

        # Placing an order
        response = self.app.post('/order', data={'product_id': 1, 'customer_email': 'test@example.com'})

        # Checking the redirect to /catalog
        self.assertEqual(response.status_code, 302)
        self.assertIn('/catalog', response.headers['Location'])

        # Checking flash message
        with self.app.session_transaction() as session:
            flashes = session.get('_flashes', [])
            self.assertTrue(any("Order placed for Laptop!" in message for _, message in flashes))
        logging.info("Flash message verified for successful order placement.")

        # Checking the addition of an order
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]['product']['name'], 'Laptop')
        logging.info("Order successfully added to the list.")

        # Testing the call to the send email function
        mock_send_email.assert_called_once_with(
            'Order Confirmation', 'test@example.com', 'Thank you for your order! You have ordered a Laptop.'
        )
        logging.info("Email function called successfully with expected parameters.")

    def test_logout(self):
        """Logout test."""
        logging.info("Starting test: test_logout")
        # User Login
        self.app.post('/', data={'username': 'user', 'password': 'password'})
        response = self.app.get('/logout')

        # Checking the redirect to the main page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.headers['Location'])
        logging.info("Logout test completed successfully.")

class TestInvalidEmailOrder(unittest.TestCase):
    """Test placing an order with an invalid email."""
    def setUp(self):
        logging.info("Setting up test client for invalid email test.")
        self.app = app.test_client()
        self.app.testing = True
        orders.clear()

    def test_order_with_invalid_email(self):
        """Test of handling invalid email."""
        logging.info("Starting test: test_order_with_invalid_email")
        # User Login
        self.app.post('/', data={'username': 'user', 'password': 'password'})
        logging.info("User logged in for invalid email test.")

        # Attempt to place an order with an invalid email
        response = self.app.post('/order', data={
            'product_id': 1,
            'customer_email': 'invalid-email'
        }, follow_redirects=True)

        # Checking flash message
        self.assertIn(b'Invalid email address. Please try again.', response.data)
        logging.info("Invalid email correctly identified and handled.")

        # Checking that the order has not been added
        self.assertEqual(len(orders), 0)
        logging.info("No order added for invalid email.")

class TestSendEmail(unittest.TestCase):
    """Test of the email sending function."""
    @patch('app.sendgrid.SendGridAPIClient')
    def test_send_email_success(self, mock_sendgrid_client):
        """Test of successful sending of email."""
        logging.info("Starting test: test_send_email_success")
        mock_response = mock_sendgrid_client.return_value.send.return_value
        mock_response.status_code = 202
        mock_response.body = 'Email sent successfully'

        # Calling the send email function
        response_code, response_body = send_email('Test Subject', 'test@example.com', 'Test body')

        self.assertEqual(response_code, 202)
        self.assertIn('Email sent successfully', response_body)
        logging.info("Email sending test completed successfully.")

if __name__ == "__main__":
    logging.info("Starting all tests...")
    unittest.main(testRunner=CustomTestRunner())
