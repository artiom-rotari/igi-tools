from collections.abc import Generator
from io import BytesIO
from pathlib import Path

import typer

from igipy import formats


def convert_all(
    reader: Generator[tuple[BytesIO, Path, Path | None]],
    parser: type[formats.base.FileModel],
    router: dict[str, Path],
    dry: bool = True,
) -> None:
    for number, (src_stream, src_path, zip_path) in enumerate(reader, start=1):
        instance = parser.model_validate_stream(src_stream)

        try:
            dst_stream, dst_suffix = instance.model_dump_stream()
        except formats.base.FileIgnored:
            continue

        if zip_path:
            dst_path = zip_path.joinpath(src_path).with_suffix(dst_suffix)
        else:
            dst_path = src_path.with_suffix(dst_suffix)

        for pattern, target_dir in router.items():
            if dst_path.match(pattern):
                dst_path = target_dir.joinpath(dst_path)
                break

        if not zip_path:
            typer.echo(
                f'Convert [{number:>05}]: "{typer.style(src_path.as_posix(), fg="green")}" '
                f'to "{typer.style(dst_path.as_posix(), fg="yellow")}"'
            )
        else:
            typer.echo(
                f'Convert [{number:>05}]: "{typer.style(src_path.as_posix(), fg="green")}" '
                f'from "{typer.style(zip_path.as_posix(), fg="red")}" '
                f'to "{typer.style(dst_path.as_posix(), fg="yellow")}"'
            )

        if not dry:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            dst_path.write_bytes(dst_stream.getvalue())
