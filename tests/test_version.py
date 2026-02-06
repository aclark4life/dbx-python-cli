"""Tests for package version."""

import dbx


def test_version_exists():
    """Test that the package has a version attribute."""
    assert hasattr(dbx, "__version__")


def test_version_format():
    """Test that the version is in the expected format."""
    assert dbx.__version__ == "0.1.0"

