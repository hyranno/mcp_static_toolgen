from typing import Any

from mcp.types import (
    AudioContent,
    BlobResourceContents,
    CallToolResult,
    ContentBlock,
    EmbeddedResource,
    ImageContent,
    TextContent,
)
from pydantic import BaseModel, json


def parse_result[T: BaseModel](model_class: type[T], result: CallToolResult) -> T:
    if result.structuredContent is not None:
        data = result.structuredContent
        return model_class.model_validate(**data)
    # Fallback: parse the text content as JSON.
    # This is for backward compatibility
    #   with tools that return structured data as text.
    (c.text for c in result.content if isinstance(c, TextContent))
    text_content = next(
        (c.text for c in result.content if isinstance(c, TextContent)), "{}"
    )
    return model_class.model_validate_json(text_content)


def dump_safe_result(result: CallToolResult) -> str:
    """
    Dump a tool result as JSON,
    but truncate any binary data (e.g. images, audio) for safety.
    """
    safe_dicts = [get_safe_content_dict(c) for c in result.content]
    return json.dumps(safe_dicts, ensure_ascii=False)


def get_safe_content_dict(content: ContentBlock) -> dict[str, Any]:
    """Dump content, but truncate any binary data (e.g. images, audio) for safety."""
    content_dict = content.model_dump(exclude_none=True)

    if isinstance(content, (ImageContent, AudioContent)):
        content_dict["data"] = f"<base64 data truncated, length={len(content.data)}>"

    elif isinstance(content, EmbeddedResource) and isinstance(
        content.resource, BlobResourceContents
    ):
        if "resource" in content_dict and "blob" in content_dict["resource"]:
            content_dict["resource"]["blob"] = (
                f"<blob data truncated, length={len(content.resource.blob)}>"
            )

    return content_dict
