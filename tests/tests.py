#!/bin/bash

from fastcli import CLI
from enum import Enum
from typing import List, Tuple

cli = CLI()

class Color(str, Enum):
    red = 'red'
    green = 'green'
    blue = 'blue'

@cli.command()
def command(x: float):
    """Docstrings are used as function descriptions."""
    print(f'x: {x} ({type(x)})')

@cli.command(name='bar', )
def foo(x: float):
    """Custom command names can be provided in the decorator."""
    command(x)

@cli.command()
def choices(color: Color = Color.green):
    """Enums are converted into an argument with fixed choices."""
    print(f'color: {color} ({type(color)})')

@cli.command()
def f(x):
    """When no type is provided, str is used as a default."""
    print(f'x: {x} ({type(x)})')

@cli.command()
def lis(l: List[str]):
    """Lists are supported."""
    print(f'l: {l} ({type(l)})')

@cli.command()
def simple(x: int, y: str, z: str = 'Default'):
    for v in x, y, z:
        print(f'v: {v} ({type(v)})')

@cli.command()
def flag(x: bool = False):
    """Boolean."""
    print(f'x: {x} ({type(x)})')

@cli.command()
def tup1(x: Tuple):
    """Tuple."""
    print(f'x: {x} ({type(x)})')

@cli.command()
def tup2(x: Tuple[int, int]):
    """Tuple."""
    print(f'x: {x} ({type(x)})')

@cli.command()
def tup3(x: Tuple[int, ...]): # Tuples komen altijd terug als list helaas, er is geen injectie punt waar de hele lijst naar float geconverteerd kan worden
    """Tuple."""
    print(f'x: {x} ({type(x)})')

@cli.command() 
def tup4(x: Tuple[()]): # Dit werkt niet
    """Empty tuple (because we can).""" # not
    print(f'x: {x} ({type(x)})')

#@cli.command() # Add to tests, must throw exception
#def tup5(x: Tuple[int, float]):
#    """Tuple."""
#    print(f'x: {x} ({type(x)})')

if __name__ == '__main__':
    ns = cli.parse_args()
