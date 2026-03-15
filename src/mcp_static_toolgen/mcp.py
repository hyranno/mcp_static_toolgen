import warnings
from dataclasses import dataclass
from typing import Any

import black
from jinja2 import Environment, PackageLoader
from langchain_mcp_adapters.sessions import Connection
from mcp import ClientSession
from mcp.types import Tool

from mcp_static_toolgen.common import (
    ParsedProperty,
    ParsedTool,
    ToolTarget,
    map_json_type_to_python,
)

warnings.filterwarnings("ignore", message=".*Pydantic V1 functionality.*")
from langchain_mcp_adapters.client import MultiServerMCPClient  # noqa: E402


@dataclass
class ParsedMCPTool(ParsedTool):
    pass


env = Environment(loader=PackageLoader(__name__, "templates"))


def parse_tools(mcp_tools: list[Tool]) -> list[ParsedMCPTool]:
    """Convert MCP tool definitions into a internal representation."""
    parsed_tools: list[ParsedMCPTool] = []

    for tool in mcp_tools:
        # tool_name -> ToolName
        class_name = "".join(word.capitalize() for word in tool.name.split("_"))
        input_props = parse_io_schema(tool.inputSchema)
        output_props = parse_io_schema(tool.outputSchema) if tool.outputSchema else None

        parsed_tools.append(
            ParsedMCPTool(
                name=tool.name,
                class_name=class_name,
                description=tool.description or "",
                input_props=input_props,
                output_props=output_props,
            )
        )

    return parsed_tools


def parse_io_schema(
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


def generate_tool_code(
    tools: list[ParsedMCPTool], target: ToolTarget = "langchain"
) -> str:
    template = env.get_template(f"{target}/mcp_tools.py.j2")
    raw_python_code = template.render(tools=tools)
    formatted_code = black.format_str(raw_python_code, mode=black.Mode())
    return formatted_code


async def fetch_tools(session: ClientSession) -> list[Tool]:
    tools_list = await session.list_tools()
    return tools_list.tools


async def connect_and_generate(
    connections: dict[str, Connection], target: ToolTarget = "langchain"
) -> dict[str, str]:
    results: dict[str, str] = {}
    client = MultiServerMCPClient(connections)
    for name, _ in connections.items():
        async with client.session(name) as session:
            await session.initialize()
            tools = await fetch_tools(session)
            parsed_tools = parse_tools(tools)
            code = generate_tool_code(parsed_tools, target)
            results[name] = code
    return results
