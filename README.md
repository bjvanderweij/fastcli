# FastCLI

FastCLI is to argparse what FastAPI is to Starlette.

FastCLI is a minimalist library inspired by FastAPI.
It allows you to define command line interfaces by writing decorated function signatures.

```
#!/bin/bash

from fastcli import CLI

cli = CLI()

@cli.command()
def simple(x: int, y: str, z: str = 'Default'):
    print(f'x: {x} ({type(x)})')
    print(f'y: {y} ({type(y)})')
    print(f'z: {z} ({type(z)})')

@cli.command(name='custom')
def also_simple(x: int, y: str, z: str = 'Default', flag: bool = False):
    """Lorum ipsum."""
    print(f'x: {x} ({type(x)})')
    print(f'y: {y} ({type(y)})')
    print(f'z: {z} ({type(z)})')

if __name__ == '__main__':
    cli.parse_args()
```

Running with the argument `custom` gives the following result:

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

* docstrings are turned into help command descriptions
* function arguments are converted into command line arguments
* types and default values are shown in the help texts
