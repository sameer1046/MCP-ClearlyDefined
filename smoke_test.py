#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from mcp_clearlydefined import server


def _print_result(title: str, payload: dict) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run smoke tests against the ClearlyDefined MCP server functions."
    )
    parser.add_argument(
        "--coordinates",
        default="pypi/pypi/-/requests/2.32.3",
        help="Coordinates used for smoke checks.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override API base URL for the test run.",
    )
    parser.add_argument(
        "--include-harvest",
        action="store_true",
        help="Also run queue_harvest (this requests real upstream work).",
    )
    args = parser.parse_args()

    if args.base_url:
        server._set_runtime_config(args.base_url, None)

    parts = args.coordinates.split("/")
    if len(parts) != 5:
        raise ValueError(
            "Coordinates must have 5 parts: type/provider/namespace/name/revision"
        )
    package_type, provider, namespace, name, revision = parts

    _print_result("get_server_config", server.get_server_config())
    _print_result(
        "get_definition",
        server.get_definition(
            package_type=package_type,
            provider=provider,
            namespace=namespace,
            name=name,
            revision=revision,
        ),
    )
    _print_result(
        "get_definition_by_coordinates",
        server.get_definition_by_coordinates(args.coordinates),
    )
    _print_result(
        "get_definitions",
        server.get_definitions([args.coordinates]),
    )

    if args.include_harvest:
        _print_result(
            "queue_harvest",
            server.queue_harvest([args.coordinates]),
        )
    else:
        print("\n=== queue_harvest ===")
        print("Skipped (pass --include-harvest to execute).")


if __name__ == "__main__":
    main()
