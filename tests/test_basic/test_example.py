"""Basic example test to validate pytest setup."""

import pytest
import os


def test_repository_structure():
    """Test that basic repository structure exists."""
    assert os.path.exists(os.path.join(os.path.dirname(__file__), '../..', 'src'))
    assert os.path.exists(os.path.join(os.path.dirname(__file__), '../..', 'README.md'))


def test_example():
    """Example test that always passes."""
    assert True