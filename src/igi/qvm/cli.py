from pathlib import Path

from typer import Typer

from ..config import Settings
from .models import QVM

app = Typer(name="igi_qvm", add_completion=False)


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


@app.command(short_help="Convert all .qvm files found in game_dir to .qsc file")
def convert_all() -> None:
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    if not settings.is_work_dir_configured():
        return

    for src_filepath in settings.game_dir.glob("**/*.qvm"):
        dst_filepath = settings.work_dir.joinpath(src_filepath.relative_to(settings.game_dir)).with_suffix(".qsc")
        dst_filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            convert(src_filepath, dst_filepath)
        except Exception as e:
            print(src_filepath)
            print(e)
