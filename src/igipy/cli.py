import string
from collections import defaultdict
from pathlib import Path
from typing import Annotated, ClassVar, Self

import typer
from pydantic import Field, PlainSerializer
from pydantic_settings import BaseSettings
from rich import print  # noqa: A004
from tabulate import tabulate

from . import __version__, formats, utils

app = typer.Typer(add_completion=False)


def main() -> None:
    app()


ConfigPath = Annotated[Path, PlainSerializer(lambda value: value.as_posix(), return_type=str, when_used="json")]


class Config(BaseSettings):
    path: ClassVar[ConfigPath] = Path("igipy.json")

    game_dir: ConfigPath = Field(default="C:/Games/ProjectIGI", description="Directory where igi.exe is located")
    archive_dir: ConfigPath = Field(default="./archive", description="Directory where .res files will be stored")
    convert_dir: ConfigPath = Field(default="./convert", description="Directory where other files will be stored")

    @classmethod
    def load(cls) -> Self:
        with cls.path.open() as fp:
            return cls.model_validate_json(fp.read())

    def is_valid(self, exit_on_error: bool = True) -> bool:  # noqa: C901, FBT001, FBT002
        valid = True

        if not self.game_dir:
            typer.echo(
                typer.style(
                    f"game_dir: is not set. Please set game dir in {self.path.as_posix()} -> game_dir",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        elif not self.game_dir.exists():
            typer.echo(
                typer.style(
                    f"game_dir: {self.game_dir.as_posix()} does not exist",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        elif not self.game_dir.is_dir():
            typer.echo(
                typer.style(
                    f"game_dir {self.game_dir.as_posix()} is not a directory",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        elif not self.game_dir.joinpath("igi.exe").is_file():
            typer.echo(
                typer.style(
                    f"game_dir: {self.game_dir.as_posix()} must point to directory that contain igi.exe",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        if not self.archive_dir:
            typer.echo(
                typer.style(
                    "archive_dir: is not set. Please set game dir in igi.json -> archive_dir",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        elif not self.archive_dir.exists():
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            typer.echo(
                typer.style(
                    f"archive_dir: {self.archive_dir.as_posix()} created",
                    fg="green",
                )
            )

        elif not self.archive_dir.is_dir():
            typer.echo(
                typer.style(
                    f"archive_dir: {self.archive_dir} is not a directory",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        if not self.convert_dir:
            typer.echo(
                typer.style(
                    f"convert_dir: is not set. Please set game dir in {self.path.as_posix()} -> convert_dir",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        elif not self.convert_dir.exists():
            self.convert_dir.mkdir(parents=True, exist_ok=True)
            typer.echo(
                typer.style(
                    f"convert_dir: {self.convert_dir.as_posix()} created",
                    fg="green",
                )
            )

        elif not self.convert_dir.is_dir():
            typer.echo(
                typer.style(
                    f"convert_dir: {self.convert_dir.as_posix()} is not a directory",
                    fg=typer.colors.YELLOW,
                )
            )
            valid = False

        if not valid and exit_on_error:
            raise typer.Exit(0)

        return valid


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", is_eager=True, help="Show version."),  # noqa: FBT001
    config: bool = typer.Option(None, "--config", is_eager=True, help="Show config."),  # noqa: FBT001
) -> None:
    if version:
        typer.echo(f"Version: {typer.style(__version__, fg='green')}")
        raise typer.Exit(0)

    if config:
        if not Config.path.exists():
            Config.path.write_text(Config().model_dump_json(indent=2))

            typer.echo(
                f"Configuration file {typer.style(Config.path.as_posix(), fg='green')} created.\n"
                f"Please open it with text editor and set {typer.style('game_dir', fg='green')} value "
                f"as directory where {typer.style('igi.exe', fg='green')} is located.\n"
                f"After execute {typer.style('igipy --config', fg='green')} again to check it."
            )
            raise typer.Exit(0)

        if not Config.path.is_file(follow_symlinks=False):
            typer.echo(
                f"Configuration file {typer.style(Config.path.as_posix(), fg='green')} exists but is not a file. "
                f"Please remove it or change its name and execute {typer.style('igipy --config', fg='green')} again."
            )
            raise typer.Exit(0)

        config_obj = Config.load()

        typer.echo(config_obj.model_dump_json(indent=2))

        config_obj.is_valid(exit_on_error=True)

        raise typer.Exit(0)

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    if not Config.path.exists():
        typer.echo(
            f"Configuration file {typer.style(Config.path.as_posix(), fg='green')} does not exist. "
            f"Please execute {typer.style('igipy --config', fg='green')} to create it. "
        )
        raise typer.Exit(0)


res_app = typer.Typer(name="res", short_help="Submodule with RES commands", add_completion=False)
app.add_typer(res_app)


@res_app.callback(invoke_without_command=True)
def res_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@res_app.command(
    name="convert-all",
    short_help="Convert all .res files found in game_dir to .zip or .json files",
)
def res_convert_all(dry: bool = False) -> None:  # noqa: FBT001, FBT002
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

    utils.convert_all(
        patterns=["**/*.res"],
        formater=formats.RES,
        src_dir=settings.game_dir,
        dst_dir={".zip": settings.archive_dir, ".json": settings.convert_dir},
        dry=dry,
    )


wav_app = typer.Typer(name="wav", short_help="Submodule with WAV commands", add_completion=False)
app.add_typer(wav_app)


@wav_app.callback(invoke_without_command=True)
def wav_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@wav_app.command(
    name="convert-all",
    short_help="Convert all .wav files found in game_dir and archive_dir to regular .wav files",
)
def wav_convert_all(dry: bool = False) -> None:  # noqa: FBT001, FBT002
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

    utils.convert_all(
        patterns=["**/*.wav"],
        formater=formats.WAV,
        src_dir=settings.game_dir,
        zip_dir=settings.archive_dir,
        dst_dir=settings.convert_dir,
        dry=dry,
    )


qvm_app = typer.Typer(name="qvm", short_help="Submodule with QVM commands", add_completion=False)
app.add_typer(qvm_app)


@qvm_app.callback(invoke_without_command=True)
def qvm_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@qvm_app.command(
    name="convert-all",
    short_help="Convert all .qvm files found in game_dir to .qsc file",
)
def qvm_convert_all(dry: bool = False) -> None:  # noqa: FBT001, FBT002
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

    utils.convert_all(
        patterns=["**/*.qvm"],
        formater=formats.QVM,
        src_dir=settings.game_dir,
        dst_dir=settings.convert_dir,
        dry=dry,
    )


tex_app = typer.Typer(
    name="tex",
    short_help="Submodule with TEX commands",
    add_completion=False,
)

app.add_typer(tex_app)


@tex_app.callback(invoke_without_command=True)
def tex_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@tex_app.command(
    name="convert-all",
    short_help="Convert all .tex, .spr and .pic files found in game_dir and archive_dir to .tga files",
)
def tex_convert_all(dry: bool = False) -> None:  # noqa: FBT001, FBT002
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

    utils.convert_all(
        patterns=["**/*.tex", "**/*.spr", "**/*.pic"],
        formater=formats.TEX,
        src_dir=Config.load().game_dir,
        zip_dir=Config.load().archive_dir,
        dst_dir=Config.load().convert_dir,
        dry=dry,
    )


# ------------------------------------------------------

dev_app = typer.Typer(
    name="dev",
    short_help="Submodule with development commands",
    add_completion=False,
)

app.add_typer(dev_app, hidden=True)


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


@dev_app.callback(invoke_without_command=True)
def dev_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@dev_app.command(short_help="List files in game directory by pattern")
def game_dir_glob(pattern: str = "**/*", absolute: bool = False) -> None:  # noqa: FBT001, FBT002
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
                print(word.decode())
            word.clear()
