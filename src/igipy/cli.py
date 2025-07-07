import string
import zipfile
from collections import defaultdict
from pathlib import Path

import typer
from pydantic import ValidationError

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
        reader=config.igi1.read_all_res(),
        parser=formats.RES,
        router={"*.zip": config.igi1.unpack_dir, "*.json": config.igi1.target_dir},
        dry=dry,
    )


@igi1_app.command(
    name="convert-all-wav",
    short_help="Convert all .wav files found in source_dir and unpack_dir to regular .wav files",
)
def igi1_convert_all_wav(dry: bool = False) -> None:
    config = Config.model_validate_file()
    utils.convert_all(
        reader=config.igi1.read_all_wav(),
        parser=formats.WAV,
        router={"*": config.igi1.target_dir},
        dry=dry,
    )


@igi1_app.command(
    name="convert-all-qvm",
    short_help="Convert all .qvm files found in source_dir to .qsc file",
)
def igi1_convert_all_qvm(dry: bool = False) -> None:
    config = Config.model_validate_file()
    utils.convert_all(
        reader=config.igi1.read_all_qvm(),
        parser=formats.QVM,
        router={"*": config.igi1.target_dir},
        dry=dry,
    )


@igi1_app.command(
    name="convert-all-tex",
    short_help="Convert all .tex, .spr and .pic files found in source_dir and unpack_dir to .tga files",
)
def igi1_convert_all_tex(dry: bool = False) -> None:
    config = Config.model_validate_file()

    utils.convert_all(
        reader=config.igi1.read_all_tex(),
        parser=formats.TEX,
        router={"*": config.igi1.target_dir},
        dry=dry,
    )


@igi1_app.command(
    name="convert-all",
    short_help="Convert all known formats found in source_dir",
)
def igi1_convert_all() -> None:
    typer.secho("Converting `.res`...", fg="green")
    igi1_convert_all_res(dry=False)
    typer.secho("Converting `.wav`...", fg="green")
    igi1_convert_all_wav(dry=False)
    typer.secho("Converting `.qvm`...", fg="green")
    igi1_convert_all_qvm(dry=False)
    typer.secho("Converting `.tex`...", fg="green")
    igi1_convert_all_tex(dry=False)


@igi1_app.command(
    name="extensions",
    short_help="Group files in source_dir and unpack_dir by extension and show counts",
    hidden=True,
)
def igi1_extensions() -> None:
    config = Config.model_validate_file()

    counter = defaultdict(lambda: {"source": 0, "unpack": 0})

    for path in config.igi1.source_dir.glob("**/*"):
        if not path.is_file():
            continue

        if path.suffix != ".dat":
            format_name = f"`{path.suffix}`"
        elif path.with_suffix(".mtp").exists():
            format_name = "`.dat` (mtp)"
        else:
            format_name = "`.dat` (graph)"

        counter[format_name]["source"] += 1

    for path in config.igi1.unpack_dir.glob("**/*.zip"):
        with zipfile.ZipFile(path, "r") as zip_file:
            for file_info in zip_file.infolist():
                format_name = f"`{Path(file_info.filename).suffix}`"
                counter[format_name]["unpack"] += 1

    results: list[tuple[str, int, int, int]] = [
        (extension, counts["source"] + counts["unpack"], counts["source"], counts["unpack"])
        for extension, counts in sorted(
            counter.items(), key=lambda item: item[1]["source"] + item[1]["unpack"], reverse=True
        )
    ]

    typer.echo(
        f"| {'Extension':<15} | {'Total':<15} | {'Source':<15} | {'Unpack':<15} |\n"
        f"|-{'-' * 15}-|-{'-' * 15}-|-{'-' * 15}-|-{'-' * 15}-|"
    )

    for extension, total, source, unpack in results:
        typer.echo(f"| {extension:<15} | {total:<15} | {source:<15} | {unpack:<15} |")


app = typer.Typer(add_completion=False)
app.add_typer(igi1_app, name="igi1", short_help="Convertors for IGI 1 game")


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
        raise typer.Exit(0)  # noqa: B904
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

        raise typer.Exit(0)  # noqa: B904

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@app.command(
    name="printable",
    short_help="Search printable series in binary files",
    hidden=True,
)
def printable(src: Path, min_length: int = 5, charset: str = string.printable) -> None:
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


def main() -> None:
    app()
