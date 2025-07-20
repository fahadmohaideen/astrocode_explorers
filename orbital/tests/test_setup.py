"""Basic test file to verify GitHub Actions setup."""
import sys

def test_basic_setup():
    """Verify that tests can run and basic assertions work."""
    assert 1 + 1 == 2, "Basic math should work"

def test_import_pytest():
    """Verify pytest is importable."""
    import pytest
    assert True, "pytest should be importable"
