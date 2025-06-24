from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from tabulate import tabulate
from typer import Typer

from ..config import Settings

app = Typer(name="igi_analyse", add_completion=False, short_help="Developer bootstrap tools")


def print_formats(counter: defaultdict):
    print(
        tabulate(
            tabular_data=sorted(counter.items(), key=lambda item: item[1], reverse=True),
            headers=["Format", "Count"],
            tablefmt="pipe",
        )
    )


@app.command(short_help="List files by pattern")
def game_dir_glob(pattern: str, relative: bool = True):
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    for number, path in enumerate(settings.game_dir.glob(pattern), start=1):
        if path.is_file():
            path_pretty = path.relative_to(settings.game_dir) if relative else path
            print(f"[{number:>04}] {path_pretty.as_posix()}")


@app.command(short_help="List formats")
def game_dir_formats():
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    formats_counter = defaultdict(lambda: 0)

    for path in settings.game_dir.glob("**/*"):
        if not path.is_file():
            continue

        if path.suffix != ".dat":
            format_name = f"`{path.suffix}`"
        elif path.with_suffix(".mtp").exists():
            format_name = "`.dat` (mtp)"
        else:
            format_name = "`.dat` (graph)"

        formats_counter[format_name] += 1

    print_formats(formats_counter)


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
def work_zip_formats(cumulative: bool = True) -> None:
    settings = Settings.load()

    if not settings.is_work_dir_configured():
        return

    formats_counter = defaultdict(lambda: 0)
    formats_per_zip_counter = defaultdict(lambda: defaultdict(lambda: 0))

    for number, path in enumerate(settings.work_dir.glob("**/*.zip"), start=1):
        with ZipFile(path) as zip_file:
            for sub_number, sub_name in enumerate(zip_file.namelist(), start=1):
                format_name = f"`{Path(sub_name).suffix}`"
                formats_counter[format_name] += 1
                formats_per_zip_counter[path.relative_to(settings.work_dir).as_posix()][format_name] += 1

    if cumulative:
        print_formats(formats_counter)
    else:
        for path, formats_counter in formats_per_zip_counter.items():
            print(path)
            print_formats(formats_counter)
            print()
