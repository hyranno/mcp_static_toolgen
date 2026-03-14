import asyncio
from typing import TypedDict

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

from mcp_toolgen.main import (
    ParsedProperty,
    ParsedTool,
    fetch_mcp_tools,
    generate_tool_code,
    parse_mcp_io_schema,
    parse_mcp_tools,
)

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


def get_mcp_tools_from_server() -> list[Tool]:
    """Connect to the MCP server and retrieve the list of tools."""
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_toolgen/tests/mock_mcp_server.py"],
    )

    async def fetch_tools(server_params: StdioServerParameters) -> list[Tool]:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await fetch_mcp_tools(session)
                return tools

    return asyncio.run(fetch_tools(server_params))


def test_parse_mcp_io_schema(snapshot: dict[str, ParsedProperty]) -> None:
    tool = mock_mcp_response[1]
    parsed_input_schema = parse_mcp_io_schema(tool.inputSchema)
    assert parsed_input_schema == snapshot


class GenerationSnapshot(TypedDict):
    parsed_tools: list[ParsedTool]
    generated_code: str


def test_generation_from_mock_tools(snapshot: GenerationSnapshot) -> None:
    assert_generation(mock_mcp_response, snapshot)


def test_generation_from_fetched_tools(snapshot: GenerationSnapshot) -> None:
    tools = get_mcp_tools_from_server()
    assert_generation(tools, snapshot)


def assert_generation(tools: list[Tool], snapshot: GenerationSnapshot) -> None:
    parsed_tools = parse_mcp_tools(tools)
    generated_code = generate_tool_code(parsed_tools)

    actual = {
        "parsed_tools": parsed_tools,
        "generated_code": generated_code,
    }
    assert actual == snapshot
