from collections.abc import Generator
from io import BytesIO
from pathlib import Path

import typer

from igipy import formats


def convert_all(
    searcher: Generator[tuple[BytesIO, Path, Path]],
    formater: type[formats.FileModel],
    dst_dir: Path | dict[str, Path],
    dry: bool = True,
) -> None:
    for i, (src_stream, src_path, src) in enumerate(searcher, start=1):
        try:
            dst_path, dst_stream = formater.model_validate_stream(src_stream).model_dump_file(src_path)
        except formats.base.FileIgnored:
            typer.echo(f"Convert [{i:>05}]: {typer.style(src.as_posix(), fg='yellow')} ignored")
            continue

        if isinstance(dst_dir, dict):
            dst = dst_dir[dst_path.suffix].joinpath(dst_path)
        elif isinstance(dst_dir, Path):
            dst = dst_dir.joinpath(dst_path)
        else:
            raise TypeError(f"dst_dir must be Path or dict[str, Path], not {type(dst_dir)}")

        typer.echo(
            f'Convert [{i:>05}]: "{typer.style(src.as_posix(), fg="green")}" '
            f'to "{typer.style(dst.as_posix(), fg="yellow")}"'
        )

        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(dst_stream.getvalue())
