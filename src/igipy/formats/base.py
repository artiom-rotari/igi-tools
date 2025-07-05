from enum import Enum
from io import BytesIO
from pathlib import Path
from struct import Struct
from typing import ClassVar, Self

from pydantic import BaseModel, NonNegativeInt


class FileModel(BaseModel):
    meta_path: Path | None = None
    meta_size: NonNegativeInt | None = None

    @classmethod
    def model_validate_file(cls, path: Path | str) -> Self:
        file_path = Path(path)
        file_bytes = file_path.read_bytes()
        file_stream = BytesIO(file_bytes)
        instance = cls.model_validate_stream(file_stream)
        instance.meta_path = file_path
        instance.meta_size = len(file_bytes)
        return instance

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        raise NotImplementedError

    def model_dump_file(self, path: Path | None = None, stream: BytesIO | None = None) -> tuple[Path, BytesIO]:
        path = path or (Path(self.meta_path.name) if self.meta_path else Path("undefined"))
        stream = stream or BytesIO()
        path, stream = self.model_dump_stream(path, stream)
        stream.seek(0)
        return path, stream

    def model_dump_stream(self, path: Path, stream: BytesIO) -> tuple[Path, BytesIO]:
        raise NotImplementedError


class FileIgnored(NotImplementedError):  # noqa: N818
    """Raise when this file is ignored intentionally"""


class StructModel(BaseModel):
    _struct: ClassVar[Struct] = None

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        cls_fields = cls.__pydantic_fields__.keys()
        cls_values = cls._struct.unpack(stream.read(cls._struct.size))
        # noinspection PyArgumentList
        return cls(**dict(zip(cls_fields, cls_values, strict=True)))


class PixelFormat(str, Enum):
    ARGB1555 = "ARGB1555"
    ARGB8888 = "ARGB8888"
