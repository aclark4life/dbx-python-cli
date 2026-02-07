"""Pytest configuration and shared fixtures."""

import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Provide a CLI runner for testing."""
    return CliRunner()
