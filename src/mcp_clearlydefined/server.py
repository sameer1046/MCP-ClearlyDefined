from __future__ import annotations

import argparse
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

DEFAULT_BASE_URL = "https://api.clearlydefined.io"
DEFAULT_TIMEOUT_SECONDS = 20.0


def _read_timeout_env() -> float:
    raw_timeout = os.getenv("CLEARLYDEFINED_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        return float(raw_timeout)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


BASE_URL = os.getenv("CLEARLYDEFINED_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
REQUEST_TIMEOUT_SECONDS = _read_timeout_env()

mcp = FastMCP("ClearlyDefined")


def _build_coordinates(
    package_type: str,
    provider: str,
    namespace: str,
    name: str,
    revision: str,
) -> str:
    safe_namespace = namespace if namespace else "-"
    return f"{package_type}/{provider}/{safe_namespace}/{name}/{revision}"


def _http_error_payload(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, httpx.HTTPStatusError):
        return {
            "ok": False,
            "error": "upstream_http_error",
            "status_code": exc.response.status_code,
            "message": str(exc),
            "response_body": exc.response.text,
        }
    if isinstance(exc, httpx.RequestError):
        return {
            "ok": False,
            "error": "network_error",
            "message": str(exc),
        }
    return {
        "ok": False,
        "error": "unexpected_error",
        "message": str(exc),
    }


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=BASE_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"accept": "application/json"},
    )


def _set_runtime_config(base_url: str | None, timeout_seconds: float | None) -> None:
    global BASE_URL, REQUEST_TIMEOUT_SECONDS
    if base_url:
        BASE_URL = base_url.rstrip("/")
    if timeout_seconds is not None:
        REQUEST_TIMEOUT_SECONDS = timeout_seconds


@mcp.tool()
def get_definition(
    package_type: str,
    provider: str,
    namespace: str,
    name: str,
    revision: str,
) -> dict[str, Any]:
    """
    Fetch one package definition from ClearlyDefined by coordinates.
    """
    coordinates = _build_coordinates(
        package_type=package_type,
        provider=provider,
        namespace=namespace,
        name=name,
        revision=revision,
    )
    return get_definition_by_coordinates(coordinates)


@mcp.tool()
def get_definition_by_coordinates(coordinates: str) -> dict[str, Any]:
    """
    Fetch one package definition from ClearlyDefined.

    Coordinates format: type/provider/namespace/name/revision
    Example: pypi/pypi/-/requests/2.32.3
    """
    try:
        with _client() as client:
            response = client.get(f"/definitions/{coordinates}")
            if response.status_code == 404:
                return {
                    "ok": False,
                    "error": "not_found",
                    "coordinates": coordinates,
                    "message": "No definition found for the provided coordinates.",
                }
            response.raise_for_status()
            return {
                "ok": True,
                "coordinates": coordinates,
                "definition": response.json(),
            }
    except Exception as exc:
        return _http_error_payload(exc)


@mcp.tool()
def get_definitions(coordinates: list[str]) -> dict[str, Any]:
    """
    Fetch multiple package definitions in one request.

    Coordinates should be a list of:
    type/provider/namespace/name/revision
    """
    try:
        with _client() as client:
            response = client.post("/definitions", json=coordinates)
            response.raise_for_status()
            return {
                "ok": True,
                "count": len(coordinates),
                "definitions": response.json(),
            }
    except Exception as exc:
        return _http_error_payload(exc)


@mcp.tool()
def queue_harvest(coordinates: list[str], tool: str = "package") -> dict[str, Any]:
    """
    Queue harvest jobs for one or more package coordinates.
    """
    payload = [{"tool": tool, "coordinates": coordinate} for coordinate in coordinates]
    try:
        with _client() as client:
            response = client.post("/harvest", json=payload)
            response.raise_for_status()
            return {
                "ok": True,
                "queued": len(coordinates),
                "tool": tool,
                "result": response.json() if response.content else {},
            }
    except Exception as exc:
        return _http_error_payload(exc)


@mcp.tool()
def get_server_config() -> dict[str, Any]:
    """
    Return the active runtime configuration for this MCP server.
    """
    return {
        "ok": True,
        "base_url": BASE_URL,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="MCP server for ClearlyDefined package definitions."
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override ClearlyDefined API base URL (e.g. https://dev-api.clearlydefined.io).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Override HTTP request timeout in seconds.",
    )
    args = parser.parse_args(argv)
    _set_runtime_config(args.base_url, args.timeout_seconds)
    mcp.run()


if __name__ == "__main__":
    main()
