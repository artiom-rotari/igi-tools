import zipfile
from collections.abc import Generator
from fnmatch import fnmatch
from io import BytesIO
from pathlib import Path

import typer

from igipy import formats


def validate_file_path_exists(path: Path | str) -> Path:
    path = Path(path)

    if not path.exists():
        typer.echo(typer.style(f"{path.as_posix()} doesn't exists", fg=typer.colors.RED))

    if not path.is_file(follow_symlinks=False):
        typer.echo(typer.style(f"{path.as_posix()} is not a file", fg=typer.colors.RED))

    return path


def validate_file_path_not_exists(path: Path) -> Path:
    path = Path(path)

    if path.exists():
        typer.echo(typer.style(f"{path.as_posix()} exists", fg=typer.colors.RED))

    return path


def search_for_convert(
    patterns: list[str],
    src_dir: Path | None = None,
    zip_dir: Path | None = None,
) -> Generator[tuple[Path, Path, BytesIO]]:
    if src_dir:
        for src in src_dir.glob("**/*"):
            for pattern in patterns:
                if fnmatch(src.as_posix(), pattern):
                    if src.is_file():
                        src_path = src.relative_to(src_dir)
                        src_stream = BytesIO(src.read_bytes())
                        yield src, src_path, src_stream

    if zip_dir:
        for zip_path in zip_dir.glob("**/*.zip"):
            with zipfile.ZipFile(zip_path, "r") as zip_file:
                for file_info in zip_file.infolist():
                    for pattern in patterns:
                        if fnmatch(file_info.filename, pattern):
                            src = zip_path.joinpath(file_info.filename)
                            src_path = src.relative_to(zip_dir)
                            src_stream = BytesIO(zip_file.read(file_info))
                            yield src, src_path, src_stream


def convert_all(
    patterns: list[str],
    formater: type[formats.FileModel],
    dst_dir: Path,
    src_dir: Path | None = None,
    zip_dir: Path | None = None,
    dry: bool = True,
) -> None:
    searcher = search_for_convert(patterns=patterns, src_dir=src_dir, zip_dir=zip_dir)

    for i, (src, src_path, src_stream) in enumerate(searcher, start=1):
        dst = dst_dir.joinpath(src_path)
        dst, dst_stream = formater.model_validate_stream(src_stream).model_dump_file(dst)

        typer.echo(
            f'Convert [{i:>05}]: "{typer.style(src.as_posix(), fg="green")}" to "{typer.style(dst.as_posix(), fg="yellow")}"'
        )

        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(dst_stream.getvalue())
