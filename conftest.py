import pytest
import os


# Set Django to allow async operations
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Customize database setup for E2E tests.
    Ensures migrations are run before tests.
    """
    pass  # django_db_setup already handles migrations