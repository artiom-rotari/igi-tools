from rich import print
from typer import Typer

from . import __version__
from .config import Settings
from .dev.cli import app as igi_dev
from .qvm.cli import app as igi_qvm
from .res.cli import app as igi_res

app = Typer(add_completion=False)
app.add_typer(igi_dev, name="dev")
app.add_typer(igi_qvm, name="qvm")
app.add_typer(igi_res, name="res")


@app.command()
def version():
    print(f"Version: [green]{__version__}[/green]")


@app.command(short_help="Initialize configuration file (igi.json)")
def config_initialize() -> None:
    Settings.dump()


@app.command(short_help="Check configuration file")
def config_check() -> None:
    settings = Settings.load()
    if settings.is_valid():
        print("[green]Configuration file is valid.[/green]")


def main() -> None:
    app()
