import string
from collections import defaultdict
from pathlib import Path

import typer
from pydantic import ValidationError
from tabulate import tabulate

from . import __version__, formats, utils
from .config import Config

igi1_app = typer.Typer(add_completion=False)


@igi1_app.callback(invoke_without_command=True)
def igi1_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@igi1_app.command(
    name="convert-all-res",
    short_help="Convert all .res files found in source_dir to .zip or .json files",
)
def igi1_convert_all_res(dry: bool = False) -> None:
    config = Config.model_validate_file()

    utils.convert_all(
        patterns=["**/*.res"],
        formater=formats.RES,
        src_dir=config.igi1.source_dir,
        dst_dir={".zip": config.igi1.unpack_dir, ".json": config.igi1.target_dir},
        dry=dry,
    )


@igi1_app.command(
    name="convert-all-wav",
    short_help="Convert all .wav files found in source_dir and unpack_dir to regular .wav files",
)
def igi1_convert_all_wav(dry: bool = False) -> None:
    config = Config.model_validate_file()

    utils.convert_all(
        patterns=["**/*.wav"],
        formater=formats.WAV,
        src_dir=config.igi1.source_dir,
        zip_dir=config.igi1.unpack_dir,
        dst_dir=config.igi1.target_dir,
        dry=dry,
    )


@igi1_app.command(
    name="convert-all-qvm",
    short_help="Convert all .qvm files found in source_dir to .qsc file",
)
def igi1_convert_all_qvm(dry: bool = False) -> None:
    config = Config.model_validate_file()

    utils.convert_all(
        patterns=["**/*.qvm"],
        formater=formats.QVM,
        src_dir=config.igi1.source_dir,
        dst_dir=config.igi1.target_dir,
        dry=dry,
    )


@igi1_app.command(
    name="convert-all-tex",
    short_help="Convert all .tex, .spr and .pic files found in source_dir and unpack_dir to .tga files",
)
def igi1_convert_all_tex(dry: bool = False) -> None:
    config = Config.model_validate_file()

    utils.convert_all(
        patterns=["**/*.tex", "**/*.spr", "**/*.pic"],
        formater=formats.TEX,
        src_dir=config.igi1.source_dir,
        zip_dir=config.igi1.unpack_dir,
        dst_dir=config.igi1.target_dir,
        dry=dry,
    )


# ------------------------------------------------------

dev_app = typer.Typer(
    name="dev",
    short_help="Submodule with development commands",
    add_completion=False,
)


def print_formats(counter: defaultdict) -> None:
    typer.echo(
        tabulate(
            tabular_data=sorted(counter.items(), key=lambda item: item[1], reverse=True),
            headers=["Format", "Count"],
            tablefmt="pipe",
        )
    )


def print_zip_formats(counter: defaultdict) -> None:
    typer.echo(
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
            typer.echo(f"[{number:>04}] {(path.absolute() if absolute else path.relative_to(directory)).as_posix()}")


@dev_app.callback(invoke_without_command=True)
def dev_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@dev_app.command(short_help="List files in game directory by pattern")
def game_dir_glob(pattern: str = "**/*", absolute: bool = False) -> None:
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

    dir_glob(directory=settings.game_dir, pattern=pattern, absolute=absolute)


@dev_app.command(short_help="List formats in game directory")
def game_dir_formats() -> None:
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

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


@dev_app.command(short_help="Search words in binary files")
def words(src: Path, min_length: int = 5, charset: str = string.printable) -> None:
    data = src.read_bytes()
    word = bytearray()

    charset = charset.encode()

    for byte in data:
        if byte in charset:
            word.append(byte)
        else:
            if len(word) >= min_length:
                typer.echo(word.decode())
            word.clear()


app = typer.Typer(add_completion=False)
app.add_typer(igi1_app, name="igi1", short_help="Convertors for IGI 1 game")
app.add_typer(dev_app, hidden=True)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", is_eager=True, help="Show version."),
) -> None:
    if version:
        typer.echo(f"Version: {typer.style(__version__, fg='green')}")
        raise typer.Exit(0)

    try:
        Config.model_validate_file()
    except FileNotFoundError:
        typer.echo(
            f"{typer.style('An error occurred!', fg='yellow')}\n"
            f"This application expects to find a configuration file at "
            f"{typer.style('`./igipy.json`', fg='yellow')}.\n"
            f"But it seems that this location already exists and is not a file.\n"
            f"Please move object somewhere else and then execute `igipy` command again.\n"
        )
        raise typer.Exit()
    except ValidationError as e:
        typer.echo(
            f"{typer.style('An error occurred!', fg='yellow')}\n"
            f"Configuration file {typer.style('`./igipy.json`', fg='yellow')} exists,"
            f"but it seems that it is not valid.\n"
            f"Open {typer.style('`./igipy.json`', fg='yellow')} using a text editor and fix errors:\n"
        )

        for error in e.errors(include_url=False):
            typer.secho(f"Error at: {'.'.join(error['loc'])}", fg="red")
            typer.secho(error["msg"])

        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


def main() -> None:
    app()
