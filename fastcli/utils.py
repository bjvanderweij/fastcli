import inspect

from typing import (Callable, Any, Optional, TypeVar, Dict, _GenericAlias,
        List, Tuple, _VariadicGenericAlias, _SpecialForm, Union, get_origin,
        get_args)

def get_function_parameters(func: Callable[..., Any]) -> Dict[str, inspect.Parameter]:
    signature = inspect.signature(func)
    return dict(signature.parameters)

def get_type_description(t: Union[type, _GenericAlias, _VariadicGenericAlias]):
    if isinstance(t, type):
        return t.__name__
    elif isinstance(get_origin(t), type):
        args = get_args(t)
        if get_origin(t) is list:
            if len(args) == 0:
                args = [str]
            return f'list of the form [{get_type_description, args[0]}, ...]'
        elif get_origin(t) is tuple:
            print(args)
            if len(args) == 0:
                return f'tuple of the form (str, ...)'
            elif len(args) == 2 and args[1] is Ellipsis:
                return f'tuple of the form ({args[0].__name__}, ...)'
            elif args == ((), ):
                args = []
            return f'tuple of the form ({", ".join(map(get_type_description, args))})'
    else:
        raise Exception()

def verify_list_or_tuple_args(list_or_tuple: Union[List, Tuple]):
    otype = get_origin(list_or_tuple)
    print(otype)
    args = get_args(list_or_tuple)
    nargs = '*'
    if otype is list:
        assert len(args) == 1
        element_type, = args
    elif otype is tuple:
        if len(args) > 0:
            element_type = args[0]
            if args[0] is ():
                element_type = str
                nargs = 0
            if not (len(args) == 2 and args[1] is Ellipsis):
                if not all(a is args[0] for a in args):
                    msg = 'tuples with different element types are unsupported'
                    raise ValueError(msg)
                nargs = len(args)
        else:
            # Default to string
            element_type = str
    return element_type, nargs

