from __future__ import annotations

import unittest

from mcp_clearlydefined import server


class ServerHelpersTest(unittest.TestCase):
    def test_build_coordinates_uses_dash_for_empty_namespace(self) -> None:
        coordinates = server._build_coordinates("pypi", "pypi", "", "requests", "2.32.3")
        self.assertEqual(coordinates, "pypi/pypi/-/requests/2.32.3")

    def test_set_runtime_config_updates_base_url_and_timeout(self) -> None:
        original_base_url = server.BASE_URL
        original_timeout = server.REQUEST_TIMEOUT_SECONDS
        try:
            server._set_runtime_config("https://dev-api.clearlydefined.io/", 45.0)
            config = server.get_server_config()
            self.assertTrue(config["ok"])
            self.assertEqual(config["base_url"], "https://dev-api.clearlydefined.io")
            self.assertEqual(config["request_timeout_seconds"], 45.0)
        finally:
            server._set_runtime_config(original_base_url, original_timeout)


if __name__ == "__main__":
    unittest.main()
