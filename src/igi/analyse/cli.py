from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from typer import Typer

from ..config import Settings

app = Typer(name="igi_analyse", add_completion=False, short_help="Developer bootstrap tools")


@app.command(short_help="List files by pattern")
def game_dir_glob(pattern: str):
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    for number, path in enumerate(settings.game_dir.glob(pattern), start=1):
        if path.is_file():
            print(f"[{number:>04}] {path.relative_to(settings.game_dir)}")


@app.command(short_help="List extensions")
def game_dir_extensions():
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    extensions_counter = defaultdict(lambda: 0)

    for path in settings.game_dir.glob("**/*"):
        if path.is_file():
            extensions_counter[path.suffix] += 1

    for extension, count in sorted(extensions_counter.items(), key=lambda item: item[1], reverse=True):
        print(f"{extension}: {count}")


@app.command(short_help="List files by pattern")
def work_dir_glob(pattern: str):
    settings = Settings.load()

    if not settings.is_work_dir_configured():
        return

    for number, path in enumerate(settings.work_dir.glob(pattern), start=1):
        if path.is_file():
            print(f"[{number:>04}] {path.relative_to(settings.work_dir)}")


@app.command(short_help="List files in zips")
def work_zip_list() -> None:
    settings = Settings.load()

    if not settings.is_work_dir_configured():
        return

    for number, path in enumerate(settings.work_dir.glob("**/*.zip"), start=1):
        print(f"[{number:>04}] {path.relative_to(settings.work_dir)}")

        with ZipFile(path) as zip_file:
            for sub_number, sub_name in enumerate(zip_file.namelist(), start=1):
                print(f"  [{sub_number:>04}] {sub_name}")


@app.command(short_help="List extensions in zips")
def work_zip_extensions(cumulative: bool = True) -> None:
    settings = Settings.load()

    if not settings.is_work_dir_configured():
        return

    extensions_counter = defaultdict(lambda: 0)
    extensions_per_zip_counter = defaultdict(lambda: defaultdict(lambda: 0))

    for number, path in enumerate(settings.work_dir.glob("**/*.zip"), start=1):
        with ZipFile(path) as zip_file:
            for sub_number, sub_name in enumerate(zip_file.namelist(), start=1):
                extensions_counter[Path(sub_name).suffix] += 1
                extensions_per_zip_counter[path.relative_to(settings.work_dir).as_posix()][Path(sub_name).suffix] += 1

    if cumulative:
        for extension, count in sorted(extensions_counter.items(), key=lambda item: item[1], reverse=True):
            print(f"{extension} {count}")
    else:
        for path, extensions_counter in extensions_per_zip_counter.items():
            print(path)

            for extension, count in sorted(extensions_counter.items(), key=lambda item: item[1], reverse=True):
                print(f"{extension} {count}")

            print()
