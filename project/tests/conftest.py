"""
Shared pytest fixtures for the silk test suite.

The autouse fixture here disables SILKY_AUTHENTICATION and SILKY_AUTHORISATION
before every test so that view-level tests can exercise the UI without setting
up a staff user. Tests that specifically assert secure-by-default behaviour
(see test_config_auth.py) re-enable the flags at the start of the test.
"""
import pytest

from silk.config import SilkyConfig


@pytest.fixture(autouse=True)
def _silk_auth_disabled_by_default():
    cfg = SilkyConfig()
    # Setting via attribute writes to the instance __dict__ (SilkyConfig's
    # __setattr__ is not overridden — the class defines __setattribute__ which
    # Python never calls). We also write to .attrs so __getattr__ fallbacks stay
    # consistent if a later test clears the instance attr.
    cfg.SILKY_AUTHENTICATION = False
    cfg.SILKY_AUTHORISATION = False
    cfg.attrs['SILKY_AUTHENTICATION'] = False
    cfg.attrs['SILKY_AUTHORISATION'] = False
    yield
