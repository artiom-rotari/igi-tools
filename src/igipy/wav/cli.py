from io import BytesIO
from pathlib import Path

from rich import print  # noqa: A004
from typer import Typer

from igipy.config import Settings
from igipy.wav.models import WAV

app = Typer(add_completion=False, short_help="Submodule with WAV commands")


@app.command(short_help="Convert InnerLoop .wav file to regular .wav file")
def convert(src: Path, dst: Path) -> BytesIO | None:
    if isinstance(src, Path) and (not src.exists() or not src.is_file()):
        print(f"{src} not found or is not a file.")
        return None

    if isinstance(dst, Path) and dst.exists():
        print(f"{dst} already exists.")
        return None

    if isinstance(src, Path):
        wav = WAV.model_validate_file(src)
    elif isinstance(src, BytesIO):
        wav = WAV.model_validate_stream(src)
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


@app.command(short_help="Convert all .wav files found in game_dir and unpacked dir to regular .wav files")
def convert_all() -> None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return

    print(f"[green]Converting .wav files from {settings.game_dir} to {settings.converted_dir}[/green]")

    for src in settings.game_dir.glob("**/*.wav"):
        dst = settings.converted_dir.joinpath(src.relative_to(settings.game_dir)).with_suffix(".wav")
        dst.parent.mkdir(parents=True, exist_ok=True)

        convert(src, dst)

    print(f"[green]Converting .wav files from {settings.unpacked_dir} to {settings.converted_dir}[/green]")

    for src in settings.unpacked_dir.glob("**/*.wav"):
        dst = settings.converted_dir.joinpath(src.relative_to(settings.unpacked_dir)).with_suffix(".wav")
        dst.parent.mkdir(parents=True, exist_ok=True)
        convert(src, dst)
