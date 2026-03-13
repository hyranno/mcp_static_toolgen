from mcp.types import Tool

from mcp_toolgen.main import (
    ParsedProperty,
    ParsedTool,
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


def test_parse_mcp_io_schema(snapshot: dict[str, ParsedProperty]) -> None:
    tool = mock_mcp_response[1]
    parsed_input_schema = parse_mcp_io_schema(tool.inputSchema)
    assert parsed_input_schema == snapshot


def test_parse_mcp_tools(snapshot: list[ParsedTool]) -> None:
    parsed_tools = parse_mcp_tools(mock_mcp_response)
    assert parsed_tools == snapshot


def test_mcp_tool_generation(snapshot: str) -> None:
    parsed_tools = parse_mcp_tools(mock_mcp_response)
    generated_code = generate_tool_code(parsed_tools)
    assert generated_code == snapshot
