import argparse
import asyncio
import os
from pathlib import Path

from langchain_mcp_adapters.sessions import Connection

from mcp_static_toolgen.mcp import connect_and_generate

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", type=Path, default=Path("generated"))


def main() -> None:
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    connections: dict[str, Connection] = {
        "mock": {
            "transport": "stdio",
            "command": "python",
            "args": ["src/mcp_static_toolgen/tests/mock_mcp_server.py"],
        },
    }
    generated_codes = asyncio.run(connect_and_generate(connections))
    for name, code in generated_codes.items():
        output_path = args.output_dir / f"{name}_mcp_tools.py"
        with open(output_path, "w") as f:
            f.write(code)


if __name__ == "__main__":
    main()
