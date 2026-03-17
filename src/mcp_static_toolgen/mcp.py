import json
import warnings
from dataclasses import dataclass
from typing import Any

import black
from datamodel_code_generator import (
    InputFileType,
    PythonVersion,
    generate,
)
from datamodel_code_generator.enums import DataModelType
from datamodel_code_generator.format import Formatter
from jinja2 import Environment, PackageLoader
from langchain_mcp_adapters.sessions import Connection
from mcp import ClientSession
from mcp.types import Tool

from mcp_static_toolgen.common import (
    ParsedTool,
    ToolTarget,
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
        input_schema_dict = parse_io_json_schema(
            tool.inputSchema, f"{class_name}InputDict", DataModelType.TypingTypedDict
        )
        output_schema_model = (
            parse_io_json_schema(
                tool.outputSchema,
                f"{class_name}Output",
                DataModelType.PydanticV2BaseModel,
            )
            if tool.outputSchema
            else None
        )

        parsed_tools.append(
            ParsedMCPTool(
                name=tool.name,
                class_name=class_name,
                description=tool.description or "",
                input_schema_dict=input_schema_dict,
                output_schema_model=output_schema_model,
            )
        )

    return parsed_tools


def parse_io_json_schema(
    schema: dict[str, Any],
    schema_name: str,
    model_type: DataModelType = DataModelType.PydanticV2BaseModel,
) -> str:
    """Convert a JSON schema into a Python TypedDict definition."""
    generated_code = generate(
        json.dumps(schema),
        class_name=schema_name,
        input_file_type=InputFileType.JsonSchema,
        output_model_type=model_type,
        target_python_version=PythonVersion.PY_314,
        use_union_operator=True,
        use_standard_collections=True,
        field_constraints=True,
        use_annotated=True,
        use_field_description=True,
        use_field_description_example=True,
        use_schema_description=True,
        disable_timestamp=True,
        use_exact_imports=True,
        custom_file_header=" ",
        formatters=[Formatter.RUFF_FORMAT, Formatter.RUFF_CHECK],
        output=None,  # We'll capture the output as a string
    )
    if not isinstance(generated_code, str):
        raise ValueError("Failed to generate code from JSON schema")
    return generated_code


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
