from enum import Enum
from io import BytesIO
from struct import Struct
from typing import ClassVar, Literal, Self

from pydantic import BaseModel, Field, NonNegativeInt

from . import base, const


class TGAImageType(int, Enum):
    NO_DATA = 0
    COLOR_MAPPED = 1
    TRUE_COLOR = 2
    BITFIELDS = 3
    RLE_COLOR_MAPPED = 9
    RLE_TRUE_COLOR = 10
    RLE_BITFIELDS = 11


class TGAHeader(base.StructModel):
    _struct: ClassVar[Struct] = Struct("<3B2HB4H2B")

    id_length: Literal[0]
    color_map_type: Literal[0]
    image_type: TGAImageType
    color_map_origin: Literal[0]
    color_map_length: Literal[0]
    color_map_depth: Literal[0]
    x_origin: Literal[0]
    y_origin: Literal[0]
    width: NonNegativeInt = Field(le=const.UINT_16.stop - 1)
    height: NonNegativeInt = Field(le=const.UINT_16.stop - 1)
    pixel_depth: Literal[8, 16, 24, 32]
    image_descriptor_alpha_depth: NonNegativeInt = Field(ge=const.UINT_04.start, le=const.UINT_04.stop - 1, default=0)
    image_descriptor_left_to_right: NonNegativeInt = Field(ge=0, le=1, default=0)
    image_descriptor_top_to_bottom: NonNegativeInt = Field(ge=0, le=1, default=0)

    @property
    def image_descriptor(self) -> int:
        return (
            (self.image_descriptor_alpha_depth & 0x0F)
            | (self.image_descriptor_left_to_right << 4)
            | (self.image_descriptor_top_to_bottom << 5)
        )

    def model_dump_stream(self, stream: BytesIO | None = None) -> BytesIO:
        stream = stream or BytesIO()

        stream.write(
            self._struct.pack(
                self.id_length,
                self.color_map_type,
                self.image_type,
                self.color_map_origin,
                self.color_map_length,
                self.color_map_depth,
                self.x_origin,
                self.y_origin,
                self.width,
                self.height,
                self.pixel_depth,
                self.image_descriptor,
            )
        )

        return stream


class TGA(BaseModel):
    header: TGAHeader
    content: bytes

    def model_dump_stream(self, stream: BytesIO | None = None) -> BytesIO:
        stream = self.header.model_dump_stream(stream)
        stream.write(self.content)
        stream.seek(0)
        return stream

    @classmethod
    def from_raw_bytes(cls, width: int, height: int, content: bytes, pixel_format: base.PixelFormat | str) -> Self:
        pixel_format = base.PixelFormat(pixel_format.upper())

        if pixel_format == base.PixelFormat.ARGB1555:
            return cls.from_raw_bytes_argb1555(width, height, content)
        if pixel_format == base.PixelFormat.ARGB8888:
            return cls.from_raw_bytes_argb8888(width, height, content)

        raise ValueError(f"Unsupported pixel format: {pixel_format}")

    @classmethod
    def from_raw_bytes_argb1555(cls, width: int, height: int, content: bytes) -> Self:
        if width not in const.UINT_16:
            raise ValueError(f"Width must be in {const.UINT_16}")

        if height not in const.UINT_16:
            raise ValueError(f"Height must be in {const.UINT_16}")

        if len(content) != width * height * 2:
            raise ValueError("Content size does not match width and height.")

        header = TGAHeader(
            id_length=0,
            color_map_type=0,
            image_type=TGAImageType.TRUE_COLOR,
            color_map_origin=0,
            color_map_length=0,
            color_map_depth=0,
            x_origin=0,
            y_origin=0,
            width=width,
            height=height,
            pixel_depth=16,
            image_descriptor_alpha_depth=1,
            image_descriptor_left_to_right=1,
            image_descriptor_top_to_bottom=1,
        )

        return cls(header=header, content=content)

    @classmethod
    def from_raw_bytes_argb8888(cls, width: int, height: int, content: bytes) -> Self:
        if width not in const.UINT_16:
            raise ValueError(f"Width must be in {const.UINT_16}")

        if height not in const.UINT_16:
            raise ValueError(f"Height must be in {const.UINT_16}")

        if len(content) != width * height * 4:
            raise ValueError("Content size does not match width and height.")

        header = TGAHeader(
            id_length=0,
            color_map_type=0,
            image_type=TGAImageType.TRUE_COLOR,
            color_map_origin=0,
            color_map_length=0,
            color_map_depth=0,
            x_origin=0,
            y_origin=0,
            width=width,
            height=height,
            pixel_depth=32,
            image_descriptor_alpha_depth=8,
            image_descriptor_left_to_right=0,
            image_descriptor_top_to_bottom=0,
        )

        return cls(header=header, content=content)
