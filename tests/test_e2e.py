import unittest
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from app import app


class TestE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Launching an application under coverage
        cls.server_process = subprocess.Popen(
            ["coverage", "run", "--parallel-mode", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(5)  # Giving the server time to start up
        # Setting Selenium WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # run without a graphical interface
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        cls.base_url = "http://localhost:5001"

    def setUp(self):
        self.driver.get(self.base_url)

    def test_login_success(self):
        self.driver.find_element(By.NAME, "username").send_keys("user")
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.TAG_NAME, "button").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("/catalog"))
        self.assertIn("Product Catalog", self.driver.page_source)

    def test_login_failure(self):
        self.driver.find_element(By.NAME, "username").send_keys("user")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpassword")
        self.driver.find_element(By.TAG_NAME, "button").click()
        error_message = self.driver.find_element(By.CLASS_NAME, "danger").text
        self.assertIn("Invalid credentials", error_message)

    def test_access_catalog_without_login(self):
        self.driver.get(f"{self.base_url}/catalog")
        self.assertIn("Please log in.", self.driver.page_source)

    def test_place_order(self):
        self.driver.find_element(By.NAME, "username").send_keys("user")
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.TAG_NAME, "button").click()
        self.driver.find_element(By.NAME, "customer_email").send_keys("test@example.com")
        self.driver.find_element(By.TAG_NAME, "button").click()
        success_message = self.driver.find_element(By.CLASS_NAME, "success").text
        self.assertIn("Order placed", success_message)

    def test_logout(self):
        self.driver.find_element(By.NAME, "username").send_keys("user")
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.TAG_NAME, "button").click()
        self.driver.find_element(By.LINK_TEXT, "Logout").click()
        self.assertIn("Logged out.", self.driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server_process.terminate()  
        cls.server_process.wait()  

if __name__ == "__main__":
    unittest.main()
