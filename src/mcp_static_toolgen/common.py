from dataclasses import dataclass
from typing import Literal


@dataclass
class ParsedTool:
    name: str
    class_name: str
    description: str
    input_schema_dict: str  # TypedDict code as string
    output_schema_model: str | None  # Pydantic model code as string or None


type ToolTarget = Literal["langchain"]
