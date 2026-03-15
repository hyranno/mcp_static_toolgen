import asyncio
import warnings
from typing import TypedDict

from mcp.types import Tool

from mcp_static_toolgen.mcp import (
    ParsedProperty,
    ParsedTool,
    connect_and_generate,
    generate_tool_code,
    parse_io_schema,
    parse_tools,
)

warnings.filterwarnings("ignore", message=".*Pydantic V1 functionality.*")
from langchain_mcp_adapters.sessions import Connection  # noqa: E402

mock_mcp_response: list[Tool] = [
    Tool(
        name="read_file",
        description="Read the complete contents of a file.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"],
        },
        outputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content of the file"},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="write_file",
        description="Write content to a file.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"},
                "append": {
                    "type": "boolean",
                    "description": "If true, append instead of overwrite",
                },
            },
            "required": ["path", "content"],
        },
    ),
]


def test_parse_io_schema(snapshot: dict[str, ParsedProperty]) -> None:
    tool = mock_mcp_response[1]
    parsed_input_schema = parse_io_schema(tool.inputSchema)
    assert parsed_input_schema == snapshot


class GenerationSnapshot(TypedDict):
    parsed_tools: list[ParsedTool]
    generated_code: str


def test_generation_from_mock_tools(snapshot: GenerationSnapshot) -> None:
    tools = mock_mcp_response
    parsed_tools = parse_tools(tools)
    generated_code = generate_tool_code(parsed_tools)

    actual = {
        "parsed_tools": parsed_tools,
        "generated_code": generated_code,
    }
    assert actual == snapshot


def test_connect_and_generation(snapshot: str) -> None:
    connections: dict[str, Connection] = {
        "mock": {
            "transport": "stdio",
            "command": "python",
            "args": ["src/mcp_static_toolgen/tests/mock_mcp_server.py"],
        },
    }
    generated_code = asyncio.run(connect_and_generate(connections))["mock"]

    assert generated_code == snapshot
