from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from struct import Struct
from typing import ClassVar, Self

from pydantic import BaseModel


class FileModel(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        """Method to load model from stream"""

    @abstractmethod
    def model_dump_stream(self) -> tuple[BytesIO, str]:
        """Method to dump model to stream"""

    @classmethod
    def model_validate_file(cls, path: Path | str) -> Self:
        return cls.model_validate_stream(BytesIO(Path(path).read_bytes()))

    def model_dump_file(self, path: Path | str) -> None:
        path = Path(path)

        stream, _ = self.model_dump_stream()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(stream.getvalue())

    @classmethod
    @abstractmethod
    def cli_decode_all(cls, config: BaseModel, pattern: str) -> None: ...

    @classmethod
    @abstractmethod
    def cli_encode_all(cls, config: BaseModel, pattern: str) -> None: ...


class FileIgnored(NotImplementedError):  # noqa: N818
    """Raise when this file is ignored intentionally"""


class StructModel(BaseModel):
    struct: ClassVar[Struct] = None

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        cls_fields = cls.__pydantic_fields__.keys()
        cls_values = cls.struct.unpack(stream.read(cls.struct.size))
        # noinspection PyArgumentList
        return cls(**dict(zip(cls_fields, cls_values, strict=True)))

    @classmethod
    def unpack_many(cls, data: bytes) -> list[Self]:
        length, remainder = divmod(len(data), cls.struct.size)

        if remainder != 0:
            raise ValueError(f"Data length {len(data)} is not divisible by struct size {cls.struct.size}")

        stream = BytesIO(data)
        return [cls.model_validate_stream(stream) for _ in range(length)]
