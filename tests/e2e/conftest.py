"""
Pytest configuration and fixtures for E2E tests.
"""
import pytest
from pathlib import Path
from .kitty_helper import KittyController


@pytest.fixture
def kitty():
    """
    Provide a KittyController instance with automatic cleanup.

    Yields:
        KittyController: Controller for kitty terminal
    """
    controller = KittyController()
    yield controller
    controller.cleanup()


@pytest.fixture
def simple_data_path(fixtures_dir):
    """
    Path to simple.tsv test data.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: Path to simple.tsv
    """
    return fixtures_dir / "e2e" / "simple.tsv"


@pytest.fixture
def numbers_data_path(fixtures_dir):
    """
    Path to numbers.tsv test data.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: Path to numbers.tsv
    """
    return fixtures_dir / "e2e" / "numbers.tsv"


@pytest.fixture
def mixed_case_data_path(fixtures_dir):
    """
    Path to mixed_case.tsv test data.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: Path to mixed_case.tsv
    """
    return fixtures_dir / "e2e" / "mixed_case.tsv"


@pytest.fixture
def sizes_data_path(fixtures_dir):
    """
    Path to sizes.tsv test data.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: Path to sizes.tsv
    """
    return fixtures_dir / "e2e" / "sizes.tsv"


@pytest.fixture
def times_data_path(fixtures_dir):
    """
    Path to times.tsv test data.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: Path to times.tsv
    """
    return fixtures_dir / "e2e" / "times.tsv"


@pytest.fixture
def empty_data_path(fixtures_dir):
    """
    Path to empty.tsv test data.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: Path to empty.tsv
    """
    return fixtures_dir / "e2e" / "empty.tsv"


@pytest.fixture
def data_gen_config_path(fixtures_dir):
    """
    Path to data_gen_test.toml config.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: Path to data_gen_test.toml
    """
    return fixtures_dir / "e2e" / "data_gen_test.toml"


# @pytest.fixture
# def aria2tui_with_simple_data(kitty, simple_data_path):
#     """
#     Launch aria2tui with simple.tsv already loaded.

#     Args:
#         kitty: KittyController instance
#         simple_data_path: Path to simple.tsv

#     Returns:
#         KittyController: Controller with listpick running
#     """
#     kitty.launch_listpick(["-i", str(simple_data_path)])
#     kitty.wait_for_text("Alice", timeout=3)
#     return kitty


@pytest.fixture
def e2e_fixtures_dir(fixtures_dir):
    """
    Return E2E fixtures directory path.

    Args:
        fixtures_dir: Root fixtures directory

    Returns:
        Path: E2E fixtures directory
    """
    return fixtures_dir / "e2e"


# Hook to save screenshot on test failure
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save screenshot on E2E test failure."""
    outcome = yield
    report = outcome.get_result()

    # Only process E2E test failures
    if report.when == "call" and report.failed:
        # Check if this is an E2E test
        if hasattr(item, "fixturenames") and "kitty" in item.fixturenames:
            # Get the kitty fixture
            kitty = item.funcargs.get("kitty")
            if kitty:
                try:
                    kitty.on_failure(item.name)
                except:
                    pass  # Don't fail if screenshot fails
