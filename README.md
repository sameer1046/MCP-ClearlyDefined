# MCP ClearlyDefined

MCP server for querying package metadata from `clearlydefined.io`.

## Features

- `get_definition`: fetch a single package definition using coordinate parts
- `get_definition_by_coordinates`: fetch a single package definition using one coordinate string
- `get_definitions`: fetch multiple package definitions in a batch
- `queue_harvest`: queue one or more harvest requests

## Setup

```bash
cd MCP-ClearlyDefined
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run server (stdio)

```bash
clearlydefined-mcp
```

Or:

```bash
python -m mcp_clearlydefined.server
```

Use `dev-api` or custom URL:

```bash
clearlydefined-mcp --base-url https://dev-api.clearlydefined.io
```

Or via environment variables:

```bash
export CLEARLYDEFINED_BASE_URL="https://dev-api.clearlydefined.io"
export CLEARLYDEFINED_TIMEOUT_SECONDS="30"
```

## MCP client config examples

### Generic / Cursor style

Add this server to your MCP config:

```json
{
  "mcpServers": {
    "clearlydefined": {
      "command": "./.venv/bin/clearlydefined-mcp",
      "args": []
    }
  }
}
```

### Claude Desktop style

```json
{
  "mcpServers": {
    "clearlydefined": {
      "command": "./.venv/bin/clearlydefined-mcp",
      "args": [
        "--base-url",
        "https://api.clearlydefined.io"
      ],
      "env": {
        "CLEARLYDEFINED_TIMEOUT_SECONDS": "20"
      }
    }
  }
}
```

### Devin / local stdio command

Use command:

```bash
./.venv/bin/clearlydefined-mcp --base-url https://api.clearlydefined.io
```

## Smoke test script

Run all read-only tools locally:

```bash
python ./smoke_test.py
```

Include harvest queueing (side-effecting request):

```bash
python ./smoke_test.py --include-harvest
```

## Run tests

```bash
python -m unittest discover -s ./tests -v
```

## Project structure

```text
MCP-ClearlyDefined/
├── src/
│   └── mcp_clearlydefined/
│       ├── __init__.py
│       └── server.py
├── tests/
│   └── test_server.py
├── smoke_test.py
├── pyproject.toml
└── README.md
```

## Coordinates format

Coordinates use:

`type/provider/namespace/name/revision`

Examples:

- `pypi/pypi/-/requests/2.32.3`
- `npm/npmjs/-/react/18.3.1`
