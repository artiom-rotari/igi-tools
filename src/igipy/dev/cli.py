from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from tabulate import tabulate
from typer import Typer

from igipy.config import Settings

app = Typer(add_completion=False, short_help="Submodule with development commands")


def print_formats(counter: defaultdict) -> None:
    print(
        tabulate(
            tabular_data=sorted(counter.items(), key=lambda item: item[1], reverse=True),
            headers=["Format", "Count"],
            tablefmt="pipe",
        )
    )


def print_zip_formats(counter: defaultdict) -> None:
    print(
        tabulate(
            tabular_data=[
                (filename, extension, count)
                for filename in sorted(counter.keys())
                for extension, count in sorted(counter[filename].items(), key=lambda item: item[1], reverse=True)
            ],
            headers=["File", "Format", "Count"],
            tablefmt="pipe",
        )
    )


def dir_glob(directory: Path, pattern: str, absolute: bool = False) -> None:
    for number, path in enumerate(directory.glob(pattern), start=1):
        if path.is_file():
            print(f"[{number:>04}] {(path.absolute() if absolute else path.relative_to(directory)).as_posix()}")


@app.command(short_help="List files in game directory by pattern")
def game_dir_glob(pattern: str = "**/*", absolute: bool = False) -> None:
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    dir_glob(directory=settings.game_dir, pattern=pattern, absolute=absolute)


@app.command(short_help="List files if work directory by pattern")
def work_dir_glob(pattern: str = "**/*", absolute: bool = False) -> None:
    settings = Settings.load()

    if not settings.is_work_dir_configured():
        return

    dir_glob(directory=settings.work_dir, pattern=pattern, absolute=absolute)


@app.command(short_help="List formats in game directory")
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


@app.command(short_help="List formats in zip files")
def work_zip_formats(cumulative: bool = True, absolute: bool = False) -> None:
    settings = Settings.load()

    if not settings.is_work_dir_configured():
        return

    formats_counter = defaultdict(lambda: 0)
    zip_formats_counter = defaultdict(lambda: defaultdict(lambda: 0))

    for number, path in enumerate(settings.work_dir.glob("**/*.zip"), start=1):
        with ZipFile(path) as zip_file:
            for sub_number, sub_name in enumerate(zip_file.namelist(), start=1):
                format_name = f"`{Path(sub_name).suffix}`"
                file_name = path.absolute().as_posix() if absolute else path.relative_to(settings.work_dir).as_posix()
                formats_counter[format_name] += 1
                zip_formats_counter[file_name][format_name] += 1

    if cumulative:
        print_formats(formats_counter)
    else:
        print_zip_formats(zip_formats_counter)
