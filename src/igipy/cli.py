from collections import defaultdict
from io import BytesIO
from itertools import chain
from pathlib import Path

import polars as pl
from rich import print  # noqa: A004
from tabulate import tabulate
from typer import Typer

from . import __version__, formats
from .config import Settings

app = Typer(add_completion=False)


def main() -> None:
    app()


@app.command()
def version() -> None:
    print(f"Version: [green]{__version__}[/green]")


@app.command(
    name="config-initialize",
    short_help="Initialize configuration file (igi.json)",
)
def config_initialize() -> None:
    Settings.dump()


@app.command(
    name="config-check",
    short_help="Check configuration file",
)
def config_check() -> None:
    settings = Settings.load()
    if settings.is_valid():
        print("[green]Configuration file is valid.[/green]")


dev_app = Typer(
    name="dev",
    short_help="Submodule with development commands",
    add_completion=False,
)

app.add_typer(dev_app)


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


@dev_app.command(short_help="List files in game directory by pattern")
def game_dir_glob(pattern: str = "**/*", absolute: bool = False) -> None:  # noqa: FBT001, FBT002
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    dir_glob(directory=settings.game_dir, pattern=pattern, absolute=absolute)


@dev_app.command(short_help="List formats in game directory")
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


res_app = Typer(
    name="res",
    short_help="Submodule with RES commands",
    add_completion=False,
)

app.add_typer(res_app)


@res_app.command(
    name="unpack",
    short_help="Unpack .res",
)
def res_unpack(src: Path, dst: Path) -> None:
    if not src.exists() and src.is_file():
        print(f"Can not read {src}. Is not a file.")
        return

    if dst.exists() and dst.is_file():
        print(f"Can not unpack to {dst}. Is a file.")
        return

    res = formats.RES.model_validate_file(src)

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


@res_app.command(
    name="unpack-all",
    short_help="Unpack all .res files found in game_dir",
)
def res_unpack_all() -> None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return

    for src_filepath in settings.game_dir.glob("**/*.res"):
        dst_filepath = settings.unpacked_dir.joinpath(src_filepath.relative_to(settings.game_dir))
        dst_filepath.mkdir(parents=True, exist_ok=True)
        print(f"[green]Unpacking {src_filepath} to {dst_filepath}[/green]")
        res_unpack(src_filepath, dst_filepath)


wav_app = Typer(
    name="wav",
    short_help="Submodule with WAV commands",
    add_completion=False,
)

app.add_typer(wav_app)


@wav_app.command(
    name="convert",
    short_help="Convert InnerLoop .wav file to regular .wav file",
)
def wav_convert(src: Path, dst: Path) -> BytesIO | None:
    if isinstance(src, Path) and (not src.exists() or not src.is_file()):
        print(f"{src} not found or is not a file.")
        return None

    if isinstance(dst, Path) and dst.exists():
        print(f"{dst} already exists.")
        return None

    if isinstance(src, Path):
        wav = formats.WAV.model_validate_file(src)
    elif isinstance(src, BytesIO):
        wav = formats.WAV.model_validate_stream(src)
    else:
        print(f"Unsupported source type: {type(src)}")
        return None

    if isinstance(dst, Path):
        dst_stream = BytesIO()
    elif isinstance(dst, BytesIO):
        dst_stream = dst
    else:
        print(f"Unsupported destination type: {type(dst)}")
        return None

    wav.to_wav(dst_stream)

    if isinstance(dst, Path):
        # noinspection PyTypeChecker
        dst.write_bytes(dst_stream.getvalue())
        print(f"Created {dst.as_posix()}")

    return dst_stream


@wav_app.command(
    name="convert-all",
    short_help="Convert all .wav files found in game_dir and unpacked dir to regular .wav files",
)
def wav_convert_all() -> None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return

    print(f"[green]Converting .wav files from {settings.game_dir} to {settings.converted_dir}[/green]")

    for src in settings.game_dir.glob("**/*.wav"):
        dst = settings.converted_dir.joinpath(src.relative_to(settings.game_dir)).with_suffix(".wav")
        dst.parent.mkdir(parents=True, exist_ok=True)

        wav_convert(src, dst)

    print(f"[green]Converting .wav files from {settings.unpacked_dir} to {settings.converted_dir}[/green]")

    for src in settings.unpacked_dir.glob("**/*.wav"):
        dst = settings.converted_dir.joinpath(src.relative_to(settings.unpacked_dir)).with_suffix(".wav")
        dst.parent.mkdir(parents=True, exist_ok=True)
        wav_convert(src, dst)


qvm_app = Typer(
    name="qvm",
    short_help="Submodule with QVM commands",
    add_completion=False,
)

app.add_typer(qvm_app)


@qvm_app.command(
    name="convert",
    short_help="Convert .qvm to .qsc file",
)
def qvm_convert(src: Path, dst: Path) -> None:
    if not src.exists() and src.is_file():
        print(f"{src} is not a file.")
        return

    if dst.exists():
        print(f"{dst} already exists.")
        return

    qvm = formats.QVM.model_validate_file(src)
    qsc = qvm.get_statement_list().get_token()

    dst.write_text(qsc)
    print(f"Created {dst.as_posix()}")


@qvm_app.command(
    name="convert-all",
    short_help="Convert all .qvm files found in game_dir to .qsc file",
)
def qvm_convert_all() -> None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return

    print(f"[green]Converting .qvm files from {settings.game_dir} to {settings.converted_dir}[/green]")

    for src_filepath in settings.game_dir.glob("**/*.qvm"):
        dst_filepath = settings.converted_dir.joinpath(src_filepath.relative_to(settings.game_dir)).with_suffix(".qsc")
        dst_filepath.parent.mkdir(parents=True, exist_ok=True)
        qvm_convert(src_filepath, dst_filepath)


tex_app = Typer(
    name="tex",
    short_help="Submodule with TEX commands",
    add_completion=False,
)

app.add_typer(tex_app)


@tex_app.command(
    name="dev",
    short_help="List .tex",
)
def tex_dev() -> pl.DataFrame | None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return None

    content = defaultdict(list)

    for directory in [settings.game_dir, settings.unpacked_dir]:
        for src in chain(
            directory.glob("**/*.tex"),
            directory.glob("**/*.spr"),
            directory.glob("**/*.pic"),
        ):
            print(src)
            tex = formats.TEX.model_validate_file(src)

            for mipmap in tex.mipmaps:
                content["level"].append(mipmap.header.level)
                content["mode"].append(mipmap.header.mode)
                content["width"].append(mipmap.header.bitmap_width)
                content["height"].append(mipmap.header.bitmap_height)

    return pl.DataFrame(content)
