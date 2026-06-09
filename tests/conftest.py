"""Global pytest configuration and shared fixtures."""
import os
import sys
import pytest

# Ensure src/ is on path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(scope="session")
def base_config():
    """Base test configuration."""
    return {
        "env": "test",
        "debug": True,
        "db_url": ":memory:",
    }


@pytest.fixture(scope="session")
def tmp_data_dir(tmp_path_factory):
    """Temporary data directory for tests that need file I/O."""
    return tmp_path_factory.mktemp("data")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with -m 'not slow')")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end (require live env)")
    config.addinivalue_line("markers", "integration: marks integration tests")
