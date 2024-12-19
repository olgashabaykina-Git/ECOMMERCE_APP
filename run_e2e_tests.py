# run_e2e_tests.py

from prometheus_client import Gauge, push_to_gateway, REGISTRY
import unittest
from tests.test_e2e import TestE2E  #

# Defining Gauges for Prometheus Metrics
tests_total_gauge = Gauge('tests_total', 'Total number of tests run')
tests_passed_gauge = Gauge('tests_passed', 'Number of tests passed')
tests_failed_gauge = Gauge('tests_failed', 'Number of tests failed')

# Global variables for tracking the number of tests
test_count = 0
tests_passed_count = 0
tests_failed_count = 0

def push_metrics():
    """
    Sending collected metrics to Prometheus Pushgateway.
    """
    global test_count, tests_passed_count, tests_failed_count
    # Update Gauges with current values
    tests_total_gauge.set(test_count)
    tests_passed_gauge.set(tests_passed_count)
    tests_failed_gauge.set(tests_failed_count)
    
    # using print instead of logging to avoid errors when closing logs
    print(f"Pushing metrics - Total: {test_count}, Passed: {tests_passed_count}, Failed: {tests_failed_count}")
    try:
        push_to_gateway('localhost:9091', job='e2e_test_job', registry=REGISTRY)
    except Exception as e:
        print(f"Failed to push metrics: {e}")

class CustomTestResult(unittest.TextTestResult):
    """
    Custom TestResult class for updating Prometheus metrics based on test results.
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
    A custom TestRunner class that uses CustomTestResult and sends metrics after tests are run.
    """
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)
    
    def run(self, test):
        """
        Override the run method to send metrics after all tests have run.
        """
        result = super().run(test)
        push_metrics()
        return result

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover('tests')  
    runner = CustomTestRunner(verbosity=2)
    runner.run(suite)
