# FastCLI

FastCLI is a minimalist library inspired by FastAPI.
It allows you to define command line interfaces by writing function signatures with type hints.
It extends argparse and is compatible with much of its functionality.

```python
#!/bin/bash

from fastcli import CLI

cli = CLI()

@cli.command()
def foo(x: int, y: str, z: str = 'Default'):
    """Lorum ipsum."""
    if VERBOSITY > 0:
        print(f'x: {x} ({type(x)})')
        print(f'y: {y} ({type(y)})')
        print(f'z: {z} ({type(z)})')
    return x, y, z

@cli.command(name='bar', aliases=['b'], description='Bar')
def bar_defition(x: int, y: str, z: str = 'Default', flag: bool = False):
    """Lorum ipsum."""
    if VERBOSITY > 0:
        print(f'x: {x} ({type(x)})')
        print(f'y: {y} ({type(y)})')
        print(f'z: {z} ({type(z)})')
    return x, y, z

if __name__ == '__main__':
    cli.add_argument(
    cli.add_argument('-v', '--verbosity', type=int, help='Set the verbosity level', choices=[-1, 0, 1], default=0)
    args = cli.parse_args()
    VERBOSITY = args.verbosity
    cli.execute()
```

FastCLI can also be used with async functions:

```python

import asyncio
from fastcli import CLI

async def afoo(x: int):
    await asyncio.sleep(x)

async def abar(x: bool = False):
    return x

if __name__ == '__main__':
    asyncio.run(cli.execute())
```


Running with the argument `custom` prints the following usage message:

```
usage: tests.py custom [-h] [--z Z] [--flag] x y

Lorum ipsum.

positional arguments:
  x           type: int
  y           type: str

optional arguments:
  -h, --help  show this help message and exit
  --z Z       type: str, default: Default
  --flag      type: bool
```

## Features

* Docstrings are turned into help command descriptions
* Function arguments are converted into command line arguments
* Types and default values are shown in the help texts

## Behaviour

FastCLI creates a command-line interface based on functions you write with the `@cli.command()` decorator.
It coerces string arguments to python types based on type hints provided in the function signatures.

Under the hood, `fastcli.CLI` is an `ArgumentParser` from the `argparse` package.
That means that most functionality that is available in argparse is available in FastCLI.
However, there are some nuances that you should be aware of.
Each function is assigned its own sub-parser such that the first positional argument determines the 

However, it is also possible to nest sub-parsers:

```python
cli = CLI()
cli.add_argument('-v', '--verbosity', type=int, help='Set the verbosity level', choices=[-1, 0, 1], default=0)
command = cli.add_command('foo') # takes care of calling cli.add_subparsers()
command.add_parameter('x', type_=int) # these methods would normally be invoked based on a function signature
command.add_parameter('y', type_=int, default)
```

Positional arguments and keyword-only arguments without a default value arguments are converted to positional command-line arguments.
Keyword arguments with a default value are converted to command-line options.

### Special behaviours

For some types, special behaviours are defined that exploit the capabilities of argparse.

#### bool

Boolean arguments with a default value of False are converted into flags.
This is achieved by creating an argument with `action="store_true"`.

#### Enum

Enumerations are converted into arguments with a fixed set of choices.
This is achieved by creating an argument with `choices=Enum.__members__.keys()`.

#### Lists, tuples and sets

Lists, tuples and sets are converted into arguments that consume a variable number of parameters.
Tuples may be defined to be of a fixed size, 
For positional arguments, it is only possible to have one positional argument if it is a list, tuple with unbounded number of elements, or set.

### Why use FastCLI?

Based on standards.

The API is the same as argparse but with some additions and shortcuts.

Very little library-specific information to be learned: works using standard python type hinting.
