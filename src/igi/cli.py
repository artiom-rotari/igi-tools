from rich import print
from typer import Typer

from . import __version__

app = Typer(add_completion=False)


@app.command()
def version():
    print(f"Version: [green]{__version__}[/green]")


def main() -> None:
    app()
