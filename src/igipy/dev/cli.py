from collections import defaultdict
from pathlib import Path

from rich import print  # noqa: A004
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


def dir_glob(directory: Path, pattern: str, absolute: bool = False) -> None:  # noqa: FBT001, FBT002
    for number, path in enumerate(directory.glob(pattern), start=1):
        if path.is_file():
            print(f"[{number:>04}] {(path.absolute() if absolute else path.relative_to(directory)).as_posix()}")


@app.command(short_help="List files in game directory by pattern")
def game_dir_glob(pattern: str = "**/*", absolute: bool = False) -> None:  # noqa: FBT001, FBT002
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    dir_glob(directory=settings.game_dir, pattern=pattern, absolute=absolute)


@app.command(short_help="List formats in game directory")
def game_dir_formats() -> None:
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
