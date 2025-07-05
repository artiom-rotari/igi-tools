import zipfile
from collections.abc import Generator
from io import BytesIO
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

    def search_for_convert_in_source(self, patterns: list[str]) -> Generator[tuple[BytesIO, Path, Path]]:
        for src_path in self.source_dir.glob("**/*"):
            for pattern in patterns:
                if src_path.is_file(follow_symlinks=False) and src_path.match(pattern):
                    src_relative = src_path.relative_to(self.source_dir)
                    src_stream = BytesIO(src_path.read_bytes())
                    yield src_stream, src_relative, src_path

    def search_for_convert_in_unpack(self, patterns: list[str]) -> Generator[tuple[BytesIO, Path, Path]]:
        for zip_path in self.unpack_dir.glob("**/*.zip"):
            with zipfile.ZipFile(zip_path, "r") as zip_file:
                for file_info in zip_file.infolist():
                    src_path = zip_path.joinpath(file_info.filename)

                    for pattern in patterns:
                        if src_path.match(pattern):
                            src_relative = src_path.relative_to(self.unpack_dir)
                            src_stream = BytesIO(zip_file.read(file_info))
                            yield src_stream, src_relative, src_path

    def res_for_convert(self) -> Generator[tuple[BytesIO, Path, Path]]:
        yield from self.search_for_convert_in_source(patterns=["**/*.res"])

    def wav_for_convert(self) -> Generator[tuple[BytesIO, Path, Path]]:
        yield from self.search_for_convert_in_source(patterns=["**/*.wav"])
        yield from self.search_for_convert_in_unpack(patterns=["**/*.wav"])

    def qvm_for_convert(self) -> Generator[tuple[BytesIO, Path, Path]]:
        yield from self.search_for_convert_in_source(patterns=["**/*.qvm"])

    def tex_for_convert(self) -> Generator[tuple[BytesIO, Path, Path]]:
        yield from self.search_for_convert_in_source(patterns=["**/*.tex", "**/*.spr", "**/*.pic"])
        yield from self.search_for_convert_in_unpack(patterns=["**/*.tex", "**/*.spr", "**/*.pic"])

    def mef_for_convert(self) -> Generator[tuple[BytesIO, Path, Path]]:
        yield from self.search_for_convert_in_unpack(patterns=["**/*.mef"])
