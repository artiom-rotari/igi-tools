import struct
from io import BytesIO
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, NonNegativeInt

from igipy.models import FileModel


class OLMHeader(BaseModel):
    unknown_01: Literal[b"\x8f\xc2\xf5\x3d\xcd\xcc\xcc\x3d"]
    created_at_year: NonNegativeInt  # 2000
    created_at_month: NonNegativeInt  # 11
    created_at_day: NonNegativeInt  # 20, 21, 22, 23
    created_at_hour: NonNegativeInt  # 0 to 23
    created_at_minute: NonNegativeInt  # 0 to 59
    created_at_second: NonNegativeInt  # 0 to 59
    created_at_millisecond: NonNegativeInt  # 0 to 999
    unknown_02: Literal[0, 1]
    unknown_03: Literal[0]
    unknown_04: Literal[0, 1]
    unknown_05: Literal[0]
    unknown_06: Literal[1]
    unknown_07: Literal[0]
    unknown_08: NonNegativeInt  # 1 to 26637
    unknown_09: Literal[0]
    unknown_10: NonNegativeInt  # 0 to 244
    unknown_11: Literal[0]
    unknown_12: NonNegativeInt  # 0 to 65516 divisible by 4
    unknown_13: NonNegativeInt  # 0 then 1218 to 3025
    unknown_14: Literal[0]
    unknown_15: Literal[0]
    unknown_16: Literal[1, 2, 4, 8, 16, 32, 64, 128, 256]
    unknown_17: Literal[1, 2, 4, 8, 16, 32, 64, 128, 256]
    unknown_18: Literal[2, 4, 8, 16, 32, 64, 128, 256, 512]  # width * 2
    unknown_19: Literal[3]
    unknown_20: Literal[0]
    unknown_21: Literal[0]
    unknown_22: Literal[0]
    unknown_23: Literal[16256]
    unknown_24: Literal[0]
    unknown_25: Literal[15616, 15744, 15872, 16000, 16128, 16256]
    unknown_26: NonNegativeInt  # 0 then 2313 to 61680
    unknown_27: NonNegativeInt  # 0 then 14208 to 15832
    unknown_28: Literal[0]
    unknown_29: Literal[0]
    unknown_30: NonNegativeInt  # from 8 to 65528 divisible by 4
    unknown_31: NonNegativeInt  # from 932 to 3594
    unknown_32: Literal[0]
    unknown_33: Literal[0]
    width: NonNegativeInt
    height: NonNegativeInt

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        data = struct.unpack("8s7I34H", stream.read(104))
        return cls(**dict(zip(cls.__pydantic_fields__.keys(), data, strict=True)))


class OLM(FileModel):
    header: OLMHeader
    content: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, path: Path = None, size: int = None) -> Self:
        header = OLMHeader.model_validate_stream(stream)
        content = stream.read(header.width * header.height * 4)

        if stream.read(1) != b"":
            message = "Parsing incomplete. Expected to reach EOF."
            raise ValueError(message)

        return cls(meta_path=path, meta_size=size, header=header, content=content)
