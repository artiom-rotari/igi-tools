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
        return cls.model_validate_stream(file_stream, path=file_path.as_posix(), size=len(file_bytes))

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, path: str | None = None, size: int | None = None) -> Self:
        raise NotImplementedError


class StructModel(BaseModel):
    _struct: ClassVar[Struct] = None

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        cls_fields = cls.__pydantic_fields__.keys()
        cls_values = cls._struct.unpack(stream.read(cls._struct.size))
        # noinspection PyArgumentList
        return cls(**dict(zip(cls_fields, cls_values, strict=True)))
