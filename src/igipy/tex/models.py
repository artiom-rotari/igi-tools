import struct
from io import BytesIO
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, NonNegativeInt

from igipy.tex.tga import bitmap_to_tga


class Bitmap(BaseModel):
    width: NonNegativeInt
    height: NonNegativeInt
    mode: NonNegativeInt
    lod: NonNegativeInt
    data: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, width: int, height: int, mode: int, lod: int) -> Self:
        if mode == 2:
            pixel_size = 2
        elif mode == 3 or mode == 67:
            pixel_size = 4
        else:
            message = f"Unsupported mode: {mode}"
            raise ValueError(message)

        lod_width = width // (1 << lod)
        lod_height = height // (1 << lod)
        data_size = lod_width * lod_height * pixel_size
        data = stream.read(data_size)

        return cls(width=width, height=height, mode=mode, lod=lod, data=data)

    def to_tga(self) -> BytesIO:
        return bitmap_to_tga(self.width, self.height, self.data)


class TEXBase(BaseModel):
    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        return cls()


class TEX2(TEXBase):
    unknown_0: NonNegativeInt
    unknown_1: NonNegativeInt
    width_line: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    mode: NonNegativeInt
    bitmap: Bitmap

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        data = struct.unpack("2I4H", stream.read(16))
        bitmap = Bitmap.model_validate_stream(stream, width=data[3], height=data[4], mode=data[5], lod=0)
        return cls(
            unknown_0=data[0],
            unknown_1=data[1],
            width_line=data[2],
            width=data[3],
            height=data[4],
            mode=data[5],
            bitmap=bitmap,
        )


class TEX6Item(BaseModel):
    unknown_0: NonNegativeInt
    unknown_1: NonNegativeInt
    unknown_2: NonNegativeInt
    unknown_3: NonNegativeInt

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, count_x: int, count_y: int) -> Self:
        data = struct.unpack("4I", stream.read(16))
        return cls(
            unknown_0=data[0],
            unknown_1=data[1],
            unknown_2=data[2],
            unknown_3=data[3],
        )


class TEX6(BaseModel):
    signature: Literal[b"LOOP"]
    version: Literal[6]
    unknown_0: NonNegativeInt
    unknown_1: NonNegativeInt
    unknown_2: NonNegativeInt
    unknown_3: NonNegativeInt
    count_x: NonNegativeInt
    count_y: NonNegativeInt
    items: list[TEX6Item]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, count: int) -> Self:
        data = struct.unpack("4sI4H2I", stream.read(24))
        items = [TEX6Item.model_validate_stream(stream, data[3], data[4]) for _ in range(count)]
        return cls(
            signature=data[0],
            version=data[1],
            unknown_0=data[2],
            unknown_1=data[3],
            unknown_2=data[4],
            unknown_3=data[5],
            count_x=data[6],
            count_y=data[7],
            items=items,
        )


class TEX9SubHeader(BaseModel):
    offset: NonNegativeInt
    mode: NonNegativeInt
    width_line: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    unknown_0: NonNegativeInt
    unknown_1: NonNegativeInt
    unknown_2: NonNegativeInt
    unknown_3: NonNegativeInt
    unknown_4: NonNegativeInt

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        data = struct.unpack("2I4H4I", stream.read(32))

        return cls(
            offset=data[0],
            mode=data[1],
            width_line=data[2],
            width=data[3],
            height=data[4],
            unknown_0=data[5],
            unknown_1=data[6],
            unknown_2=data[7],
            unknown_3=data[8],
            unknown_4=data[9],
        )


class TEX9(TEXBase):
    unknown_0: NonNegativeInt
    unknown_1: NonNegativeInt
    unknown_2: NonNegativeInt
    unknown_3: NonNegativeInt
    unknown_4: NonNegativeInt
    offset: NonNegativeInt
    count: NonNegativeInt
    unknown_5: NonNegativeInt
    width: NonNegativeInt
    height: NonNegativeInt
    mode: NonNegativeInt
    sub_headers: list[TEX9SubHeader]
    bitmaps: list[Bitmap]
    footer: TEX6

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header_data = struct.unpack("11I", stream.read(44))

        sub_headers = [TEX9SubHeader.model_validate_stream(stream) for _ in range(header_data[6])]

        bitmaps = [
            Bitmap.model_validate_stream(
                stream, width=header_data[8], height=header_data[9], mode=header_data[10], lod=0
            )
            for _ in range(header_data[6])
        ]

        footer = TEX6.model_validate_stream(stream, count=header_data[6])

        if stream.read(1) != b"":
            message = "Parsing incomplete. Expected to reach EOF."
            raise ValueError(message)

        return cls(
            unknown_0=header_data[0],
            unknown_1=header_data[1],
            unknown_2=header_data[2],
            unknown_3=header_data[3],
            unknown_4=header_data[4],
            offset=header_data[5],
            count=header_data[6],
            unknown_5=header_data[7],
            width=header_data[8],
            height=header_data[9],
            mode=header_data[10],
            sub_headers=sub_headers,
            bitmaps=bitmaps,
            footer=footer,
        )


class TEX11(TEXBase):
    pass


class TEX(BaseModel):
    signature: Literal[b"LOOP"]
    version: Literal[2, 9, 11]
    content: TEX2 | TEX9 | TEX11

    @classmethod
    def model_validate_file(cls, path: Path | str) -> Self:
        # noinspection PyTypeChecker
        return cls.model_validate_stream(BytesIO(Path(path).read_bytes()))

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        signature, version = struct.unpack("4sI", stream.read(8))

        if version == 2:  # noqa: PLR2004
            return cls(signature=signature, version=version, content=TEX2.model_validate_stream(stream))

        if version == 9:  # noqa: PLR2004
            return cls(signature=signature, version=version, content=TEX9.model_validate_stream(stream))

        if version == 11:  # noqa: PLR2004
            return cls(signature=signature, version=version, content=TEX11.model_validate_stream(stream))

        message = f"Unsupported version: {version}"
        raise ValueError(message)
