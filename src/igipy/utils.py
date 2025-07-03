from pathlib import Path

import typer


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
