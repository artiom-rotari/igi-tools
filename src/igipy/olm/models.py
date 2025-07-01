from io import BytesIO
from pathlib import Path
from struct import Struct
from typing import ClassVar, Literal, Self

from pydantic import Field, NonNegativeInt

from igipy.models import FileModel, StructModel


class OLM(FileModel):
    header: "OLMHeader"
    item_headers: list["OLMItemHeader"]
    item_contents: list[bytes]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, path: Path | None = None, size: int | None = None) -> Self:
        header = OLMHeader.model_validate_stream(stream)
        item_headers = [OLMItemHeader.model_validate_stream(stream) for _ in range(header.count)]
        item_contents = [stream.read(item_header.width * item_header.height * 4) for item_header in item_headers]

        if stream.read(1) != b"":
            raise ValueError("Parsing incomplete. Expected to reach EOF.")

        return cls(
            meta_path=path,
            meta_size=size,
            header=header,
            item_headers=item_headers,
            item_contents=item_contents,
        )


class OLMHeader(StructModel):
    _struct: ClassVar[Struct] = Struct("4s4s7I6I")

    unknown_01: Literal[b"\x8f\xc2\xf5\x3d"]
    unknown_02: Literal[b"\xcd\xcc\xcc\x3d"]
    created_at_year: NonNegativeInt  # 2000
    created_at_month: NonNegativeInt  # 11
    created_at_day: NonNegativeInt  # 20, 21, 22, 23
    created_at_hour: NonNegativeInt  # 0 to 23
    created_at_minute: NonNegativeInt  # 0 to 59
    created_at_second: NonNegativeInt  # 0 to 59
    created_at_millisecond: NonNegativeInt  # 0 to 999
    unknown_03: Literal[0, 1]
    unknown_04: Literal[0, 1]
    count: NonNegativeInt = Field(ge=1)
    unknown_06: NonNegativeInt  # 1 to 57090
    unknown_07: NonNegativeInt  # 0 to 224
    unknown_08: NonNegativeInt  # 0 then 79835332 to 198291324


class OLMItemHeader(StructModel):
    _struct: ClassVar[Struct] = Struct("22H")

    unknown_01: Literal[0]
    unknown_02: Literal[0]
    unknown_03: Literal[1, 2, 4, 8, 16, 32, 64, 128, 256]  # equal to width
    unknown_04: Literal[1, 2, 4, 8, 16, 32, 64, 128, 256]
    unknown_05: Literal[2, 4, 8, 16, 32, 64, 128, 256, 512]
    unknown_06: Literal[3]
    unknown_07: Literal[0]
    unknown_08: Literal[0]
    unknown_09: Literal[0]
    unknown_10: Literal[16256]
    unknown_11: Literal[0]
    unknown_12: Literal[15616, 15744, 15872, 16000, 16128, 16256]
    unknown_13: NonNegativeInt
    unknown_14: NonNegativeInt
    unknown_15: Literal[0]
    unknown_16: Literal[0]
    unknown_17: NonNegativeInt  # Always divisible by 8
    unknown_18: NonNegativeInt  # from 932 to 3594
    unknown_19: Literal[0]
    unknown_20: Literal[0]
    width: Literal[1, 2, 4, 8, 16, 32, 64, 128, 256]
    height: Literal[1, 2, 4, 8, 16, 32, 64, 128, 256]
