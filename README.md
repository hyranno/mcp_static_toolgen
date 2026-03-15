# MCP-Toolgen

Static binding code generator for MCP tools.

## Background

Most MCP integrations fetch tool schemas **dynamically at runtime**. While flexible, this makes it impossible to use static type checkers, breaks IDE autocompletion, and introduces "runtime surprises" when upstream schemas change.

This project is a **static bindgen** for MCP. It connects to an MCP server once and generates strictly typed Python code. By moving tool resolution from **runtime to build-time**, you get:

* **Full Type Safety**: Catch interface mismatches with `mypy` or `pyright` before execution.

* **IDE Support**: Enjoy perfect autocompletion for tool arguments.

* **Determinism**: Your agent's interface is locked in code, making it auditable and production-ready.

## Usage
#### Install
```
uv add mcp_static_toolgen
```

#### Code Generation
```python
import asyncio
from langchain_mcp_adapters.sessions import Connection
from mcp_static_toolgen.mcp import connect_and_generate

connections: dict[str, Connection] = {
    "mock": {
        "transport": "stdio",
        "command": "python",
        "args": ["src/mcp_static_toolgen/tests/mock_mcp_server.py"],
    },
}
generated_codes = asyncio.run(connect_and_generate(connections))
```
See `example` for complete example.
