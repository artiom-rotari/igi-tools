from io import BytesIO
from pathlib import Path
from typing import Self

from pydantic import BaseModel
from pydantic.v1 import NonNegativeInt


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
