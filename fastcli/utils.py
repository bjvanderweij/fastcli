import inspect

from typing import Callable, Any, Optional, TypeVar, Dict
from pydantic.typing import ForwardRef, evaluate_forwardref


# Copied from FastAPI code
def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


# Copied from FastAPI code
def get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


def get_arguments(func: Callable[..., Any]):
    signature = get_typed_signature(func)
    return dict(signature.parameters)
    #return {name: param.annotation for name, param in signature.params.items()}

