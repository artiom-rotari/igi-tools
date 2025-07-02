import struct
from io import BytesIO
from struct import Struct
from typing import ClassVar, Literal, Self, Union

from pydantic import BaseModel, NonNegativeInt

from igipy.formats import base


class TEX(base.FileModel):
    variant: Union["TEX02", "TEX07", "TEX09", "TEX11"]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, path: str | None = None, size: int | None = None) -> Self:
        signature, version = struct.unpack("4sI", stream.read(8))

        stream.seek(0)

        if version == 2:
            variant = TEX02.model_validate_stream(stream)
        elif version == 7:
            variant = TEX07.model_validate_stream(stream)
        elif version == 9:
            variant = TEX09.model_validate_stream(stream)
        elif version == 11:
            variant = TEX11.model_validate_stream(stream)
        else:
            raise ValueError(f"Unsupported version: {version}")

        return cls(meta_path=path, meta_size=size, variant=variant)

    @property
    def mipmaps(self) -> list["Mipmap"]:
        if isinstance(self.variant, TEX02):
            return [self.variant.content]
        if isinstance(self.variant, TEX07) or isinstance(self.variant, TEX09):
            return self.variant.item_contents
        if isinstance(self.variant, TEX11):
            return self.variant.content
        raise ValueError(f"Unsupported variant: {self.variant}")


class TEX02(BaseModel):
    header: "TEX02Header"
    content: "Mipmap"

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header = TEX02Header.model_validate_stream(stream)
        content = Mipmap.model_validate_stream(stream, width=header.width, height=header.height, mode=header.mode)

        if stream.read(1) != b"":
            raise ValueError("Parsing incomplete. Expected to reach EOF.")

        return cls(header=header, content=content)


class TEX07(BaseModel):
    header: "TEX07Header"
    item_headers: list["TEX07ItemHeader"]
    item_contents: list["Mipmap"]
    footer: "TEX06"

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header = TEX07Header.model_validate_stream(stream)
        item_headers = [TEX07ItemHeader.model_validate_stream(stream) for _ in range(header.count)]
        item_contents = [
            Mipmap.model_validate_stream(
                stream,
                width=header.width,
                height=header.height,
                mode=header.mode,
            )
            for _ in range(header.count)
        ]
        footer = TEX06.model_validate_stream(stream)

        if stream.read(1) != b"":
            raise ValueError("Parsing incomplete. Expected to reach EOF.")

        return cls(header=header, item_headers=item_headers, item_contents=item_contents, footer=footer)


class TEX09(BaseModel):
    header: "TEX09Header"
    item_headers: list["TEX09ItemHeader"]
    item_contents: list["Mipmap"]
    footer: "TEX06"

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header = TEX09Header.model_validate_stream(stream)
        item_headers = [TEX09ItemHeader.model_validate_stream(stream) for _ in range(header.count)]
        item_contents = [
            Mipmap.model_validate_stream(
                stream,
                width=header.width,
                height=header.height,
                mode=header.mode,
            )
            for _ in range(header.count)
        ]
        footer = TEX06.model_validate_stream(stream)

        if stream.read(1) != b"":
            raise ValueError("Parsing incomplete. Expected to reach EOF.")

        return cls(header=header, item_headers=item_headers, item_contents=item_contents, footer=footer)


class TEX11(BaseModel):
    header: "TEX11Header"
    content: list["Mipmap"]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header = TEX11Header.model_validate_stream(stream)
        content = list()

        for level in range(10):
            position = stream.tell()

            if stream.read(1) == b"":
                break

            stream.seek(position)

            content.append(
                Mipmap.model_validate_stream(
                    stream,
                    width=header.width,
                    height=header.height,
                    mode=header.mode,
                )
            )

        if stream.read(1) != b"":
            raise ValueError("Parsing incomplete. Expected to reach EOF.")

        return cls(header=header, content=content)


class TEX06(BaseModel):
    header: "TEX06Header"
    content: list["TEX06Content"]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header = TEX06Header.model_validate_stream(stream)
        content = [TEX06Content.model_validate_stream(stream) for _ in range(header.count_x * header.count_y)]
        return cls(header=header, content=content)


class TEX02Header(base.StructModel):
    _struct: ClassVar[Struct] = Struct("4sI8H")

    signature: Literal[b"LOOP"]
    version: Literal[2]
    unknown_01: NonNegativeInt
    unknown_02: NonNegativeInt
    unknown_03: NonNegativeInt
    unknown_04: NonNegativeInt
    unknown_05: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    mode: NonNegativeInt


class TEX07Header(base.StructModel):
    _struct: ClassVar[Struct] = Struct("4s12I")

    signature: Literal[b"LOOP"]
    version: Literal[7]
    unknown_01: NonNegativeInt
    unknown_02: NonNegativeInt
    unknown_03: NonNegativeInt
    unknown_04: NonNegativeInt
    unknown_05: NonNegativeInt
    offset: NonNegativeInt
    count: NonNegativeInt
    unknown_06: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    mode: NonNegativeInt


class TEX09Header(TEX07Header):
    version: Literal[9]


class TEX11Header(base.StructModel):
    _struct: ClassVar[Struct] = Struct("4s4I6H")

    signature: Literal[b"LOOP"]
    version: Literal[11]
    mode: NonNegativeInt
    unknown_01: NonNegativeInt
    unknown_02: NonNegativeInt
    unknown_03: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    unknown_04: NonNegativeInt
    unknown_05: NonNegativeInt
    unknown_06: NonNegativeInt


class Mipmap(BaseModel):
    class Header(BaseModel):
        level: NonNegativeInt
        mode: NonNegativeInt
        width: NonNegativeInt
        height: NonNegativeInt

        @property
        def bitmap_width(self) -> int:
            return self.width // (1 << self.level)

        @property
        def bitmap_height(self) -> int:
            return self.height // (1 << self.level)

        @property
        def bitmap_depth(self) -> int:
            return {2: 2, 3: 4, 67: 4}[self.mode]

    header: Header
    bitmap: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, width: int, height: int, mode: int, level: int = 0) -> Self:
        header = cls.Header(level=level, mode=mode, width=width, height=height)
        bitmap = stream.read(header.bitmap_width * header.bitmap_height * header.bitmap_depth)
        return cls(header=header, bitmap=bitmap)


class TEX06Header(base.StructModel):
    _struct: ClassVar[Struct] = Struct("4sI4H2I")

    signature: Literal[b"LOOP"]
    version: Literal[6]
    unknown_01: NonNegativeInt
    unknown_02: NonNegativeInt
    unknown_03: NonNegativeInt
    unknown_04: NonNegativeInt
    count_x: NonNegativeInt
    count_y: NonNegativeInt


class TEX06Content(base.StructModel):
    _struct: ClassVar[Struct] = Struct("4I")

    unknown_01: NonNegativeInt
    unknown_02: NonNegativeInt
    unknown_03: NonNegativeInt
    unknown_04: NonNegativeInt


class TEX07ItemHeader(base.StructModel):
    _struct: ClassVar[Struct] = Struct("2I16H")

    offset: NonNegativeInt
    unknown_01: NonNegativeInt
    width: NonNegativeInt
    unknown_02: NonNegativeInt
    height: NonNegativeInt
    unknown_03: NonNegativeInt
    unknown_04: NonNegativeInt
    unknown_05: NonNegativeInt
    unknown_06: NonNegativeInt
    unknown_07: NonNegativeInt
    unknown_08: NonNegativeInt
    unknown_09: NonNegativeInt
    unknown_10: NonNegativeInt
    unknown_11: NonNegativeInt
    unknown_12: NonNegativeInt
    unknown_13: NonNegativeInt
    unknown_14: NonNegativeInt
    unknown_15: NonNegativeInt


class TEX09ItemHeader(base.StructModel):
    _struct: ClassVar[Struct] = Struct("2I4H4I")

    offset: NonNegativeInt
    mode: NonNegativeInt
    unknown_01: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    unknown_02: NonNegativeInt
    unknown_03: NonNegativeInt
    unknown_04: NonNegativeInt
    unknown_05: NonNegativeInt
    unknown_06: NonNegativeInt
