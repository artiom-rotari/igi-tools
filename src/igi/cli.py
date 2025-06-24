from rich import print
from typer import Typer

from . import __version__
from .analyse.cli import app as igi_analyse
from .config.cli import app as igi_config
from .res.cli import app as igi_res

app = Typer(add_completion=False)
app.add_typer(igi_analyse, name="analyse")
app.add_typer(igi_config, name="config")
app.add_typer(igi_res, name="res")


@app.command()
def version():
    print(f"Version: [green]{__version__}[/green]")


def main() -> None:
    app()
