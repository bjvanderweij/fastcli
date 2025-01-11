from argparse import ArgumentParser, ArgumentError, Action
import inspect

from .utils import get_type_description, get_function_parameters, verify_list_or_tuple_args

from typing import (Callable, Any, Dict, Optional, TypeVar, _SpecialForm, _GenericAlias,
        Iterable, Tuple, Union, List, get_origin, get_args, get_type_hints, Type)
from enum import Enum, Flag

# TODO:
# * Merge the two classes below so you can do sub_cli = cli.add_command(.....), sub_cli.add_command() (kinda like routers)
# * Add support for pydantic and parsing from JSON

# Copied from FastAPI
DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])


class UnionValidator:
    
    def __init__(self, type_):
        self.type_ = type_

    def __call__(self, arg: str):
        for t in get_args(self.type_):
            if t is None:
                continue
            try:
                return t(arg)
            except ValueError:
                pass
        raise ValueError(f'could cast to none of {", ".join(map(str, get_args(self.type_)))}')

    def __str__(self):
        return f'validator of {repr(self.type_)}'

def basic_type(type_, incl_none=False):
    return (type_ in (int, str, bool) + ((type(None), ) if incl_none else ())
            or isinstance(type_, type) and issubclass(type_, Enum)) 


def is_supported_type(type_) -> bool:
    if basic_type(type_):
        return True
    if get_origin(type_) is Union:
        if all(basic_type(t, incl_none=True) for t in get_args(type_)):
            return True
    if isinstance(type_, type) and issubclass(type_, Enum):
        return True
    if get_origin(type_) in [list, tuple, set]:
        if all(basic_type(t) for t in get_args(type_)):
            return True

class CommandParameter:

    _empty = inspect._empty

    def __init__(
            self,
            name: str,
            type_: Type[Any],
            default: Any,
            help_: str = '',
        ) -> None:
        # If the type is of the form Optional[Type] and we have 
        # a default value, set type_ to Type
        if default != self._empty and get_origin(type_) is Union:
            args = get_args(type_)
            if len(args) == 2 and type(None) in args:
                try:
                    type_ = args[(args.index(type(None)) + 1) % 2]
                except ValueError:
                    pass
        if not is_supported_type(type_):
            raise ValueError(f'unsupported type: {type_}')
        self.name = name
        self.type_ = type_
        self.default = default
        self.help_ = help_

    @property
    def dest(self) -> str:
        if self.default is self._empty:
            return self.name
        return f'--{self.name}'

    @property
    def kwargs(self) -> Dict:
        kwargs = dict(
                type=self.type_
            )
        if self.type_ is bool and self.default is False:
            kwargs['action'] = 'store_true'
            kwargs.pop('type')
        elif self.default is not self._empty:
            kwargs['default'] = self.default
        if isinstance(self.type_, type) and issubclass(self.type_, Enum):
            kwargs['choices'] = list(self.type_.__members__.keys())
        # TODO: Handle Optional, Unions, etc.
        elif isinstance(get_origin(self.type_), type) and (
                    issubclass(get_origin(self.type_), list) 
                    or issubclass(get_origin(self.type_), tuple)
                ):
            element_type, nargs = verify_list_or_tuple_args(self.type_)
            kwargs['nargs'] = nargs
            kwargs['type'] = element_type
        elif (get_origin(self.type_) is Union
                and all(isinstance(t, type) for t in get_args(self.type_))):
            kwargs['type'] = UnionValidator(self.type_)
        elif isinstance(self.type_, type):
            pass # all good
        kwargs['help'] = self._help_text(kwargs)
        return kwargs

    def _help_text(self, kwargs) -> str: # TODO: use HelpFormatter instead?
        default_help = ''
        if 'default' in kwargs:
            default_help = f', default: {kwargs["default"]}'
        extra_help = f' type: {self._type_name}{default_help}'
        return self.help_ + extra_help

    @property
    def _type_name(self) -> str:
        if isinstance(self.type_, type):
            return self.type_.__name__
        elif get_origin(self.type_) is Union:
            return f'Union of {",".join(map(lambda t: t.__name__, get_args(self.type_)))}'
        elif isinstance(get_origin(self.type_), type):
            return get_type_description(self.type_)

    #def cast_inp(self, inp: Union[str, List[str]]) -> Any:
    #    if isinstance(self.type_, type):
    #        return self.type_(inp)
    #    elif isinstance(self.type_, _SpecialForm):
    #        raise ValueError('special forms are not supported.')
        #elif isinstance(get_origin(self.type_), type) and (
        #            issubclass(get_origin(self.type_), list) 
        #            or issubclass(get_origin(self.type_), tuple)
        #        ):
        #    otype = get_origin(self.type_)
        #    args = get_args(self.type_)
        #    if otype is list:
        #        assert len(args) == 1
        #        element_types = args[0]
        #    elif otype is tuple:
        #        homogenous_var_length = False
        #        if len(args) > 0:
        #            if len(args) == 2 and args[1] is Ellipsis:
        #                element_types = args[0]
        #            elif len(args) > 0 and len(inp) != len(args):
        #                msg = f'must provide {len(args)} arguments, not {len(inp)}'
        #                raise ArgumentError(self.name, msg)
        #            else:
        #                element_types = args
        #        else:
        #            # Default to string
        #            element_types = str
        #    else:
        #        print(otype)
        #        raise ValueError(f'unsupported type: {self.type_}')
        #    assert isinstance(element_types, type) or all(isinstance(t, type) for t in element_types)
        #    if isinstance(element_types, list):
        #        return [t(e) for e, t in zip(element_types, inp)]
        #    else:
        #        return [element_types(e) for e in inp]

#class _FunctionSubParsersAction(_SubParsersAction):
#
#    def __call__(self, parser, namespace, values, execute=False, option_string=None) -> None:
#        super().__call__(*args, **kwargs)
#        parser_name = values[0]
#        parser = self.name_parser_map[parser_name]
#        self.namespace._function = parser.

class CLI(ArgumentParser):

    def __init__(
            self,
            *args, 
            description: Optional[str] = None,
            func: Callable[..., Any] = None,
            **kwargs
        ):
        super().__init__(
                *args,
                description=description or inspect.cleandoc(func.__doc__ or ""),
                **kwargs
            )
        self.parameters = {}
        self._kwargs = None

    def set_function(self, func):
        self.set_defaults(_command=self)
        self.func = func
        type_hints = get_type_hints(func)
        for name, param in get_function_parameters(func).items():
            # Default to string when no annotation is provided
            type_ = str if name not in type_hints else type_hints[name]
            self.add_parameter(name, type_, param.default)
    
    def add_parameter(self, name, type_, default=CommandParameter._empty) -> Action:
        parameter = CommandParameter(name, type_, default)
        self.parameters[name] = parameter
        return self.add_argument(parameter.dest, **parameter.kwargs)

    def parse_known_args(self, args, namespace):
        args, argv = super().parse_known_args(args, namespace)
        # Do some post-hox type conversions
        for param in self.parameters.values():
            # Convert tuple types
            if get_origin(param.type_) is tuple:
                setattr(args, param.name, get_origin(param.type_)(getattr(args, param.name)))
            # TODO: convert and validate tuple sub-types?
            # TODO: no, do this in _check value and maintain a counter....
        return args, argv

    def add_function_parsers(self, **kwargs):
        return self.add_subparsers(parser_class=type(self), required=True, **kwargs)

    def add_command(
            self,
            func: Callable[..., Any], 
            name: Optional[str] = None,
            aliases: Iterable = (),
            description: Optional[str] = None,
            **kwargs
        ) -> ArgumentParser:
        if self._subparsers is None:
            self.subparsers = self.add_function_parsers()
        name = name or func.__name__
        parser = self.subparsers.add_parser(name, aliases=aliases, description=description)
        parser.set_function(func)
        return parser

    def command(
                self,
                name: str = None,
                aliases: Iterable = (),
                description: str = None
            ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: Callable[..., Any]) -> DecoratedCallable:
            self.add_command(
                    func,
                    name=name,
                    description=description,
                    aliases=aliases
                )
            return func
        return decorator

    def execute(self, namespace=None):
        if namespace is None:
            namespace = self.parse_args()
            return namespace._command.execute(namespace)
        else:
            kwargs = vars(namespace)
            return self.func(**{name: kwargs[name] for name in self.parameters.keys()})

