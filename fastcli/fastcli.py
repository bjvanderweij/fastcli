import argparse
import inspect

from utils import get_arguments, get_type_description
from typing import Callable, Any, Optional, TypeVar, _SpecialForm, get_origin
from enum import Enum, Flag

# TODO:
# * Merge the two classes below so you can do sub_cli = cli.add_command(.....), sub_cli.add_command() (kinda like routers)
# * Add support for pydantic and parsing from JSON

# Copied from FastAPI
DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])

class CLI(argparse.ArgumentParser):

    def __init__(self, *args, func=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.subparsers = None

    def add_command(
                self,
                func: Callable[..., Any], 
                name: str = None,
                type_encoders: dict = {}
            ) -> None:
        if self.subparsers is None:
            self.subparsers = self.add_subparsers(parser_class=Command)
        name = name or func.__name__
        return self.subparsers.add_parser(name, func=func)

    def command(
                self,
                name: str = None
            ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_command(
                    func,
                    name=name,
                )
            return func
        return decorator


class Command(CLI):

    def __init__(
                self,
                func: Callable[..., Any],
                *args, 
                description: Optional[str] = None,
                **kwargs
            ):
        super().__init__(
                *args,
                description=description or inspect.cleandoc(func.__doc__ or ""),
                **kwargs)
        self.func = func
        arguments = get_arguments(func)
        for arg, param in arguments.items():
            # Default to string when no annotation is provided
            param_type = str if param.annotation == inspect._empty else param.annotation
            dest = f'--{arg}'
            kwargs = dict(
                    type=param_type,
                )
            if param.default is param.empty:
                dest = arg
            elif param_type == bool and param.default == False:
                kwargs['action'] = 'store_true'
                kwargs.pop('type')
            else:
                kwargs['default'] = param.default
            if isinstance(param_type, _SpecialForm):
                raise ValueError('Special forms are not supported.')
            elif isinstance(param_type, type):
                type_name = param_type.__name__
                if issubclass(param_type, Enum):
                    kwargs['choices'] = list(param_type.__members__.keys())
            elif isinstance(get_origin(param_type), type):
                type_name = get_type_description(param_type)
            default_help = ''
            if 'default' in kwargs:
                default_help = f', default: {kwargs["default"]}'
            extra_help = f' type: {type_name}{default_help}'
            kwargs['help'] = kwargs.get('help', '') +  extra_help
            self.add_argument(dest, **kwargs)

    def parse_known_args(self, args, namespace):
        args, argv = super().parse_known_args(args, namespace)
        self.func(**vars(args))
        return args, argv

