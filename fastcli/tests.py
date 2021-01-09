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
