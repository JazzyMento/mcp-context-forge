"""Helper for validating MCP Gateway health responses"""


def is_gateway_healthy(response_json: object) -> bool:
    """Return True when the gateway health response reports healthy status"""
    if not isinstance(response_json, dict):
        return False

    return response_json.get("status") == "healthy"
