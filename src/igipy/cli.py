from rich import print  # noqa: A004
from typer import Typer

from . import __version__
from .config import Settings
from .dev.cli import app as igi_dev
from .qvm.cli import app as igi_qvm
from .res.cli import app as igi_res
from .wav.cli import app as igi_wav

app = Typer(add_completion=False)
app.add_typer(igi_dev, name="dev")
app.add_typer(igi_qvm, name="qvm")
app.add_typer(igi_res, name="res")
app.add_typer(igi_wav, name="wav")


@app.command()
def version() -> None:
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
