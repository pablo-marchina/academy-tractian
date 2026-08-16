from __future__ import annotations

from typing import Any
from .models import BoundRequest, ExecutionBinding

MODEL_CONTROLLED_FIELDS = frozenset({"x-user-id", "user_id", "seed"})


def validate_model_arguments(arguments: dict[str, Any]) -> None:
    forbidden = sorted(k for k in arguments if k in MODEL_CONTROLLED_FIELDS)
    if forbidden:
        raise ValueError(f"model-controlled identity/environment fields are forbidden: {forbidden}")


def bind_request(*, method: str, path: str, arguments: dict[str, Any], binding: ExecutionBinding) -> BoundRequest:
    validate_model_arguments(arguments)
    query = dict(arguments.get("query", {}))
    body = arguments.get("body")
    if binding.seed is not None:
        query["seed"] = binding.seed
    return BoundRequest(method=method, path=path, query=query, headers={"x-user-id": binding.user_id}, body=body)
