import pytest
from prometheus_client import CollectorRegistry, REGISTRY

@pytest.fixture(scope="function", autouse=True)
def reset_prometheus_registry():
    """
    Replace the default Prometheus registry with a new one before each test.
    This prevents conflicts caused by previously registered metrics.
    """
    # Create a new registry and replace the default one
    new_registry = CollectorRegistry()
    REGISTRY.__init__()  # Reinitialize the default registry
    REGISTRY._collector_to_names = new_registry._collector_to_names
    REGISTRY._names_to_collectors = new_registry._names_to_collectors
