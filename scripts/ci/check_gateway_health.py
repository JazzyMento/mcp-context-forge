"""Helper for validating MCP Gateway health responses"""

from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def is_gateway_healthy(status_code: int, response_json: object) -> bool:
    """Return True when the gateway health endpoint returns HTTP 200 and healthy status."""
    if status_code != 200:
        return False

    if not isinstance(response_json, dict):
        return False

    return response_json.get("status") == "healthy"


def check_gateway_health_url(url: str, timeout: int = 10) -> bool:
    """Call a gateway health URL and validate the HTTP status and JSON response."""
    try:
        with urlopen(url, timeout=timeout) as response:
            status_code = response.getcode()
            response_body = response.read().decode("utf-8")
            response_json = json.loads(response_body)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return False

    return is_gateway_healthy(status_code, response_json)


def main() -> int:
    """Run the gateway health check from the command line."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/ci/check_gateway_health.py <health-url>")
        return 2

    health_url = sys.argv[1]

    if check_gateway_health_url(health_url):
        print("Gateway health check passed: endpoint returned HTTP 200 and status=healthy")
        return 0

    print("Gateway health check failed: expected HTTP 200 and status=healthy")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
