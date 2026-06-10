"""Unit tests for the gateway health response validation helper.

These tests check that the gateway is only treated as healthy when the /health endpoint responds
HTTP 200 and {"status": "healthy"}.

Any other HTTP status, unhealthy response, incomplete response or invalid response
is treated as NOT healthy.
"""

from scripts.ci.check_gateway_health import is_gateway_healthy


def test_http_200_and_healthy_response_returns_true():
    response = {"status": "healthy"}

    assert is_gateway_healthy(200, response) is True


def test_http_500_and_healthy_response_returns_false():
    response = {"status": "healthy"}

    assert is_gateway_healthy(500, response) is False


def test_http_200_and_unhealthy_response_returns_false():
    response = {"status": "unhealthy"}

    assert is_gateway_healthy(200, response) is False


def test_http_200_and_missing_status_returns_false():
    response = {"message": "ok"}

    assert is_gateway_healthy(200, response) is False


def test_http_200_and_non_dictionary_response_returns_false():
    response = "healthy"

    assert is_gateway_healthy(200, response) is False
