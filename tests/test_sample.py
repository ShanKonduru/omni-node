"""Sample tests to verify OmniNode setup."""

def test_sample():
    """Verify basic test infrastructure."""
    assert True


def test_import_backend():
    """Test backend imports work."""
    from backend.core.config import get_settings
    settings = get_settings()
    assert settings.app_name == "OmniNode"


def test_import_models():
    """Test database models import."""
    from backend.models.models import User, MCPServer, ToolCache
    assert User is not None
    assert MCPServer is not None
    assert ToolCache is not None


def test_namespace_resolver_import():
    """Test namespace resolver imports."""
    from backend.services.namespace_resolver import NamespaceResolver, AmbiguityError
    assert NamespaceResolver is not None
    assert AmbiguityError is not None

