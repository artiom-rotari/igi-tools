from typer import Typer

from . import Settings

app = Typer(name="igi_config", add_completion=False, short_help="Configure CLI")


@app.command(short_help="Initialize configuration file (igi.json)")
def initialize() -> None:
    Settings.dump()


@app.command(short_help="Check configuration file")
def check() -> None:
    settings = Settings.load()
    settings.check()
