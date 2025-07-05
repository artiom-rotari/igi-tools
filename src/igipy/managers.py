from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, PlainSerializer, field_validator

PosixPath = Annotated[Path, PlainSerializer(lambda value: value.as_posix(), return_type=str, when_used="json")]


class BaseManager(BaseModel):
    pass


class IGI1Manager(BaseManager):
    source_dir: PosixPath = Path("C:/Games/ProjectIGI")
    unpack_dir: PosixPath = Path("./unpack")
    target_dir: PosixPath = Path("./target")

    # noinspection PyNestedDecorators
    @field_validator("source_dir", mode="after")
    @classmethod
    def is_game_dir(cls, value: Path) -> Path:
        if not value.is_dir():
            raise ValueError(f"{value.as_posix()} is not a directory")

        if not (value / "igi.exe").is_file(follow_symlinks=False):
            raise ValueError(f"igi.exe not found in {value.as_posix()}")

        return value

    # noinspection PyNestedDecorators
    @field_validator("unpack_dir", "target_dir", mode="after")
    @classmethod
    def is_work_dir(cls, value: Path) -> Path:
        if not value.exists():
            value.mkdir(parents=True)

        if not value.is_dir():
            raise ValueError(f"{value.as_posix()} is not a directory")

        return value
