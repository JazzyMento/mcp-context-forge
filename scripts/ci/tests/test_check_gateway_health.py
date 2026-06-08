"""Unit tests for the gateway health response validation helper

These tests check that only a valid {"status": "healthy"} response is treated
as healthy; unhealthy, incomplete or invalid responses return False
"""

from scripts.ci.check_gateway_health import is_gateway_healthy


def test_healthy_response_returns_true():
    response = {"status": "healthy"}
    assert is_gateway_healthy(response) is True


def test_unhealthy_response_returns_false():
    response = {"status": "unhealthy"}
    assert is_gateway_healthy(response) is False


def test_missing_status_returns_false():
    response = {"message": "ok"}
    assert is_gateway_healthy(response) is False


def test_non_dictionary_response_returns_false():
    response = "healthy"
    assert is_gateway_healthy(response) is False
