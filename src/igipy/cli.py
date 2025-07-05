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


def main() -> None:
    app()
