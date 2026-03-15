from dataclasses import dataclass
from typing import Literal


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


type ToolTarget = Literal["langchain"]
