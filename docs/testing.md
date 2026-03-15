# Testing Guide — where2sit

## Testing Framework
We use **pytest** with **pytest-django** for all automated testing.

## How to Run Tests Locally (Make sure your virtual environment is activated)

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with code coverage report
pytest --cov=rooms --cov-report=term -v

# Run a specific test file
pytest rooms/tests.py

# Run a specific test class
pytest rooms/tests.py::TestRoomModel

# Run a single test
pytest rooms/tests.py::TestRoomModel::test_create_room