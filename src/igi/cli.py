from rich import print
from typer import Typer

from . import __version__
from .config.cli import app as igi_config
from .game.cli import app as igi_game
from .res.cli import app as igi_res

app = Typer(add_completion=False)
app.add_typer(igi_config, name="config")
app.add_typer(igi_game, name="game")
app.add_typer(igi_res, name="res")


@app.command()
def version():
    print(f"Version: [green]{__version__}[/green]")


def main() -> None:
    app()
