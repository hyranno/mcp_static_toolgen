from dataclasses import dataclass
from typing import Any

import black
from jinja2 import Environment, PackageLoader
from mcp.types import Tool


@dataclass
class ParsedProperty:
    python_type: str
    description: str
    required: bool


@dataclass
class ParsedTool:
    name: str
    class_name: str
    description: str
    input_props: dict[str, ParsedProperty]
    output_props: dict[str, ParsedProperty] | None


env = Environment(loader=PackageLoader(__name__, "templates"))


def map_json_type_to_python(json_type: str) -> str:
    mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
    }
    return mapping.get(json_type, "Any")


def parse_mcp_tools(mcp_tools: list[Tool]) -> list[ParsedTool]:
    """Convert MCP tool definitions into a internal representation."""
    parsed_tools: list[ParsedTool] = []

    for tool in mcp_tools:
        # tool_name -> ToolName
        class_name = "".join(word.capitalize() for word in tool.name.split("_"))
        input_props = parse_mcp_io_schema(tool.inputSchema)
        output_props = (
            parse_mcp_io_schema(tool.outputSchema) if tool.outputSchema else None
        )

        parsed_tools.append(
            ParsedTool(
                name=tool.name,
                class_name=class_name,
                description=tool.description or "",
                input_props=input_props,
                output_props=output_props,
            )
        )

    return parsed_tools


def parse_mcp_io_schema(
    schema: dict[str, Any],
) -> dict[str, ParsedProperty]:
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])

    parsed_props: dict[str, ParsedProperty] = {}
    for prop_name, prop_details in properties.items():
        parsed_props[prop_name] = ParsedProperty(
            python_type=map_json_type_to_python(prop_details.get("type", "string")),
            description=prop_details.get("description", ""),
            required=prop_name in required_fields,
        )
    return parsed_props


def generate_tool_code(tools: list[ParsedTool]) -> str:
    template = env.get_template("langchain/mcp_tools.py.j2")
    raw_python_code = template.render(tools=tools)
    formatted_code = black.format_str(raw_python_code, mode=black.Mode())
    return formatted_code


def main() -> None:
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

    parsed_tools = parse_mcp_tools(mock_mcp_response)

    formatted_code = generate_tool_code(parsed_tools)

    output_path = "generated_mcp_tools.py"
    with open(output_path, "w") as f:
        f.write(formatted_code)

    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
