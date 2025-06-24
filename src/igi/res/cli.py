from io import BytesIO
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

from typer import Typer

from ..config import Settings
from .models import RES

app = Typer(name="igi_res", add_completion=False)


@app.command()
def inspect(src: Path) -> None:
    res = RES.model_validate_file(src)

    for name_chunk, body_chunk in res.content:
        filename = name_chunk.get_cleaned_content().removeprefix("LOCAL:")
        content = body_chunk.get_cleaned_content()
        print(filename, len(content))


@app.command(short_help="Convert .res file to .zip file")
def convert(src: Path, dst: Path) -> None:
    if not src.exists() and src.is_file():
        print(f"{src} is not a file.")
        return

    if dst.exists():
        print(f"{dst} already exists.")
        return

    res = RES.model_validate_file(src)

    if not res.is_archive():
        print(f"{src} is not a archive.")
        return

    dst_file = BytesIO()
    with ZipFile(dst_file, "w", compression=ZIP_STORED) as zip_file:
        for name_chunk, body_chunk in res.content:
            if body_chunk.header.signature == b"PATH":
                continue

            filename = name_chunk.get_cleaned_content().removeprefix("LOCAL:")
            content = body_chunk.get_cleaned_content()
            zip_file.writestr(filename, content)

    dst_file.seek(0)
    dst_data = dst_file.read()

    # noinspection PyTypeChecker
    dst.write_bytes(dst_data)


@app.command(short_help="Convert all .res files found in game_dir to .zip")
def convert_all() -> None:
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    if not settings.is_work_dir_configured():
        return

    for src_filepath in settings.game_dir.glob("**/*.res"):
        dst_filepath = settings.work_dir.joinpath(src_filepath.relative_to(settings.game_dir)).with_suffix(".zip")
        dst_filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            convert(src_filepath, dst_filepath)
        except Exception as e:
            print(src_filepath)
            print(e)
