
"""Shared fixtures for the test suite."""

import pytest

from src.app import app as flask_app


@pytest.fixture(name='client')
def client_fixture():
    """Flask test client, so no test needs a running server."""
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()
