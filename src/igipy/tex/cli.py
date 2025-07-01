from collections import defaultdict

from rich import print  # noqa: A004
from typer import Typer

from igipy.config import Settings
from igipy.tex.models import TEX

app = Typer(add_completion=False, short_help="Submodule with TEX commands")


@app.command(short_help="List .tex")
def dev() -> None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return

    metrics = defaultdict(list)

    for directory in [settings.game_dir, settings.unpacked_dir]:
        for src in directory.glob("**/*.tex"):
            tex = TEX.model_validate_file(src)
            metrics[tex.version].append(src.as_posix())

    for key, value in metrics.items():
        print(f"[green]{key}[/green]: {len(value)}")
        print(*value, sep="\n")
