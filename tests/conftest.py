"""Global pytest configuration and shared fixtures."""
import os
import sys
import pytest

# Ensure src/ is on path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# Modules that require external dependencies (NEXUS, src.citizens, etc.)
# These tests are skipped during collection to avoid ImportError
INTEGRATION_TEST_MODULES = {
    "autoresearch",
    "breakthroughs",
    "performance",
    "test_browser_bridge",
    "test_cdp_capabilities",
    "test_comet_degraded_mode",
    "test_controller",
    "test_env2_tab_harvest",
    "test_event_bus",
    "test_joker_engine",
    "test_meta_framework",
    "test_model",
    "test_nexus_engines_completion",
    "test_ontological_memory",
    "test_PrfaaSProviderCitizen",
    "test_qoderwork_citizen",
    "test_quantum_mstgf_citizen_e2e",
    "test_service",
    "test_triad_convergence",
    "test_vector_engine",
}


def pytest_ignore_collect(collection_path, config):
    """Ignore test modules that require external dependencies."""
    module_name = collection_path.stem
    if module_name in INTEGRATION_TEST_MODULES:
        return True
    # Also ignore subdirectories that are integration-only
    parts = collection_path.parts
    if "autoresearch" in parts or "breakthroughs" in parts:
        return True
    return False


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
