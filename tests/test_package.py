"""Tests for src.omni_node package initialization."""

import pytest


def test_package_import():
    """Test that the omni_node package can be imported."""
    import src.omni_node
    assert src.omni_node is not None


def test_package_version():
    """Test package version attribute."""
    from src.omni_node import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_package_name():
    """Test package name attribute."""
    from src.omni_node import __name__ as pkg_name
    assert pkg_name == "src.omni_node"
