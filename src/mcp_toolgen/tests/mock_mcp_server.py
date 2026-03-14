from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("MockServer")


class ReadFileOutput(BaseModel):
    content: str = Field(..., description="Content of the file")


@mcp.tool()
def read_file(
    path: Annotated[str, Field(description="Path to the file")],
) -> ReadFileOutput:
    """Read the complete contents of a file."""
    return ReadFileOutput(content=f"Mock content for file {path}")


@mcp.tool()
def write_file(
    path: Annotated[str, Field(description="Path to the file")],
    content: Annotated[str, Field(description="Content to write")],
    append: Annotated[
        bool | None, Field(description="If true, append instead of overwrite")
    ] = None,
) -> str:
    """Write content to a file."""
    return "Success"


if __name__ == "__main__":
    mcp.run(transport="stdio")
