from pathlib import Path

from rich import print
from typer import Typer

from igi.config import Settings
from igi.res.models import RES

app = Typer(add_completion=False, short_help="Submodule with RES commands")


@app.command(short_help="Unpack .res")
def unpack(src: Path, dst: Path) -> None:
    if not src.exists() and src.is_file():
        print(f"Can not read {src}. Is not a file.")
        return

    if dst.exists() and dst.is_file():
        print(f"Can not unpack to {dst}. Is a file.")
        return

    res = RES.model_validate_file(src)

    if res.is_text_container():
        print(f"{src} skipped because it is a text container.")
        return

    if res.is_file_container():
        for res_file in res.content:
            if not res_file.is_file():
                continue

            res_file_path = dst.joinpath(res_file.file_name)
            res_file_path.parent.mkdir(parents=True, exist_ok=True)

            if res_file_path.exists():
                print(f"{res_file_path} already exists.")
                continue

            res_file_path.write_bytes(res_file.file_content)
            print(f"Created {res_file_path}")


@app.command(short_help="Unpack all .res files found in game_dir")
def unpack_all() -> None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return

    for src_filepath in settings.game_dir.glob("**/*.res"):
        dst_filepath = settings.unpacked_dir.joinpath(src_filepath.relative_to(settings.game_dir))
        dst_filepath.mkdir(parents=True, exist_ok=True)
        print(f"[green]Unpacking {src_filepath} to {dst_filepath}[/green]")
        unpack(src_filepath, dst_filepath)
