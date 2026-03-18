from collections.abc import Mapping
from typing import Any, get_type_hints

from pydantic import BaseModel, create_model


def create_model_from_typeddict(
    name: str, td: type[Mapping[str, Any]]
) -> type[BaseModel]:
    hints = get_type_hints(td, include_extras=True)
    return create_model(name, **hints)
