from pathlib import Path

from rich import print
from typer import Typer

from igi.config import Settings
from igi.qvm.models import QVM

app = Typer(add_completion=False, short_help="Submodule with QVM commands")


@app.command(short_help="Convert .qvm to .qsc file")
def convert(src: Path, dst: Path) -> None:
    if not src.exists() and src.is_file():
        print(f"{src} is not a file.")
        return

    if dst.exists():
        print(f"{dst} already exists.")
        return

    qvm = QVM.model_validate_file(src)
    qsc = qvm.get_statement_list().get_token()

    dst.write_text(qsc)
    print(f"Created {dst.as_posix()}")


@app.command(short_help="Convert all .qvm files found in game_dir to .qsc file")
def convert_all() -> None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return

    print(f"[green]Converting .qvm files from {settings.game_dir} to {settings.converted_dir}[/green]")

    for src_filepath in settings.game_dir.glob("**/*.qvm"):
        dst_filepath = settings.converted_dir.joinpath(src_filepath.relative_to(settings.game_dir)).with_suffix(".qsc")
        dst_filepath.parent.mkdir(parents=True, exist_ok=True)
        convert(src_filepath, dst_filepath)
