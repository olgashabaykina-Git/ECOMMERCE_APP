import unittest
from unittest.mock import patch
from app import app, users, products, send_email, order_placed_notification
import logging
import sys
from app import app

import os
os.environ['COVERAGE_RUN'] = 'true' 

# Configure logging to both file and console
unit_test_logger = logging.getLogger("unit_tests")
unit_test_logger.setLevel(logging.INFO)

# Remove existing handlers to prevent duplication
if unit_test_logger.hasHandlers():
    unit_test_logger.handlers.clear()

# File handler for unit test logs
file_handler = logging.FileHandler("unit_test_app.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Console handler for unit test logs
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add handlers to the logger
unit_test_logger.addHandler(file_handler)
unit_test_logger.addHandler(console_handler)


class TestApp(unittest.TestCase):

    def setUp(self):
        unit_test_logger.info("Setting up test client for TestApp.")
        self.app = app.test_client()
        self.app.testing = True

    def test_login_success(self):
        unit_test_logger.info("Starting test: test_login_success")
        response = self.app.post('/', data={'username': 'user', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Redirect to catalog expected
        with self.app.session_transaction() as sess:
            self.assertIn('user', sess)
        unit_test_logger.info("Test login_success completed successfully.")

    def test_login_failure(self):
        unit_test_logger.info("Starting test: test_login_failure")
        response = self.app.post('/', data={'username': 'user', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)  # Expected to stay on the same page
        self.assertIn(b'Invalid credentials. Please try again.', response.data)
        unit_test_logger.info("Test login_failure completed with expected invalid credentials message.")

    def test_catalog_access_without_login(self):
        unit_test_logger.info("Starting test: test_catalog_access_without_login")
        response = self.app.get('/catalog')
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        unit_test_logger.info("Unauthorized catalog access redirected as expected.")

    def test_order_without_login(self):
        unit_test_logger.info("Starting test: test_order_without_login")
        response = self.app.post('/order', data={'product_id': 1, 'customer_email': 'test@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.headers['Location'])
        unit_test_logger.info("Order attempt without login redirected as expected.")

    @patch('app.send_email')
    def test_order_placed(self, mock_send_email):
        unit_test_logger.info("Starting test: test_order_placed")
        mock_send_email.return_value = (202, 'Email sent successfully')
        with self.app:
            self.app.post('/', data={'username': 'user', 'password': 'password'})
            unit_test_logger.info("User logged in for order placement.")
            response = self.app.post('/order', data={'product_id': 1, 'customer_email': 'test@example.com'})
            
            # Check that a redirect has occurred to /catalog
            self.assertEqual(response.status_code, 302)
            self.assertIn('/catalog', response.headers['Location'])
            unit_test_logger.info("Order placed successfully and redirected to catalog.")
            
            # Checking flash messages
            with self.app.session_transaction() as session:
                flashes = session['_flashes']  
                self.assertTrue(
                    any("Order placed for Laptop!" in message for category, message in flashes),
                    "Flash message about order placement is missing!"
                )
            unit_test_logger.info("Flash message verified for successful order placement.")

    def test_logout(self):
        unit_test_logger.info("Starting test: test_logout")
        with self.app:
            self.app.post('/', data={'username': 'user', 'password': 'password'})
            unit_test_logger.info("User logged in for logout test.")
            response = self.app.get('/logout')
            self.assertEqual(response.status_code, 302)
            self.assertIn('/', response.headers['Location'])
            unit_test_logger.info("Logout test completed successfully.")

class TestEmail(unittest.TestCase):
    # Testing the email sending function
    @patch('app.sendgrid.SendGridAPIClient')
    def test_send_email_success(self, mock_sendgrid_client):
        unit_test_logger.info("Starting test: test_send_email_success")
        mock_response = mock_sendgrid_client.return_value.send.return_value
        mock_response.status_code = 202
        mock_response.body = 'Email sent successfully'
        
        # Call the email sending function and check the result
        response_code, response_body = send_email('Test Subject', 'test@example.com', 'Test body')
        self.assertEqual(response_code, 202)
        self.assertIn('Email sent successfully', response_body)
        unit_test_logger.info("Email sending test completed successfully.")

    @patch('app.sendgrid.SendGridAPIClient')
    def test_order_placed_notification(self, mock_sendgrid_client):
        unit_test_logger.info("Starting test: test_order_placed_notification")
        mock_response = mock_sendgrid_client.return_value.send.return_value
        mock_response.status_code = 202
        mock_response.body = 'Email sent successfully'
     
        # Test data for order1
        order = {"user": "user", "product": {"name": "Laptop"}}
        
        response_code, response_body = order_placed_notification(order, 'test@example.com')
        self.assertEqual(response_code, 202)
        self.assertIn('Email sent successfully', response_body)
        unit_test_logger.info("Order placed notification test completed successfully.")

if __name__ == "__main__":
    unit_test_logger.info("Starting all unit tests...")
    unittest.main()