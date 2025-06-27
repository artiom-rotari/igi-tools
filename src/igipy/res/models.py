import struct
from io import BytesIO
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, Field, NonNegativeInt


class ChunkHeader(BaseModel):
    signature: bytes = Field(min_length=4, max_length=4)
    length: NonNegativeInt
    padding: Literal[4, 32]
    next_position: NonNegativeInt

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        # noinspection PyTypeChecker
        data = struct.unpack("4s3I", stream.read(16))
        return cls(signature=data[0], length=data[1], padding=data[2], next_position=data[3])


class Chunk(BaseModel):
    header: ChunkHeader
    content: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, header: ChunkHeader) -> Self:
        padding_length = (header.padding - stream.tell() % header.padding) % header.padding
        padding_data = stream.read(padding_length)

        if padding_data != b"\x00" * padding_length:
            raise ValueError(f"Expected padding data to be null bytes: {padding_data}")

        content = stream.read(header.length)

        return cls(header=header, content=content)


class RESChunkNAMEHeader(ChunkHeader):
    signature: Literal[b"NAME"]


class RESChunkNAME(Chunk):
    header: RESChunkNAMEHeader

    def get_cleaned_content(self) -> str:
        return self.content.decode().removesuffix("\x00")


class RESChunkBODYHeader(ChunkHeader):
    signature: Literal[b"BODY", b"PATH", b"CSTR"]


class RESChunkBODY(Chunk):
    header: RESChunkBODYHeader

    def get_cleaned_content(self) -> bytes | str:
        if self.header.signature == b"BODY":
            return self.content
        if self.header.signature in {b"PATH", b"CSTR"}:
            return self.content.decode().removesuffix("\x00")
        raise ValueError("Invalid signature")


class RESHeader(BaseModel):
    signature: Literal[b"ILFF"]
    length: NonNegativeInt
    padding: Literal[4, 32]
    next_position: NonNegativeInt
    content_signature: Literal[b"IRES"]


class RESFile(BaseModel):
    name: RESChunkNAME
    body: RESChunkBODY

    def is_file(self) -> bool:
        return self.body.header.signature == b"BODY"

    def is_text(self) -> bool:
        return self.body.header.signature == b"CSTR"

    def is_path(self) -> bool:
        return self.body.header.signature == b"PATH"

    @property
    def file_name(self) -> str:
        if not self.is_file():
            raise ValueError("File is not a file")
        return self.name.get_cleaned_content().removeprefix("LOCAL:")

    @property
    def file_content(self) -> bytes | str:
        if not self.is_file():
            raise ValueError("File is not a file")
        return self.body.get_cleaned_content()


class RES(BaseModel):
    header: RESHeader
    content: list[RESFile]

    @classmethod
    def model_validate_file(cls, path: Path | str) -> Self:
        # noinspection PyTypeChecker
        return cls.model_validate_stream(BytesIO(Path(path).read_bytes()))

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        # noinspection PyTypeChecker
        header_data = struct.unpack("4s3I4s", stream.read(20))

        header = RESHeader(
            signature=header_data[0],
            length=header_data[1],
            padding=header_data[2],
            next_position=header_data[3],
            content_signature=header_data[4],
        )

        padding_length = (header.padding - stream.tell() % header.padding) % header.padding
        padding_data = stream.read(padding_length)

        if padding_data != b"\x00" * padding_length:
            raise ValueError(f"Expected padding data to be null bytes: {padding_data}")

        content = []

        while True:
            position = stream.tell()
            name_chunk = RESChunkNAME.model_validate_stream(stream, RESChunkNAMEHeader.model_validate_stream(stream))
            stream.seek(position + name_chunk.header.next_position)

            position = stream.tell()
            body_chunk = RESChunkBODY.model_validate_stream(stream, RESChunkBODYHeader.model_validate_stream(stream))
            stream.seek(position + body_chunk.header.next_position)

            content.append(RESFile(name=name_chunk, body=body_chunk))

            if body_chunk.header.next_position == 0:
                break

        return cls(header=header, content=content)

    def is_file_container(self) -> bool:
        return all(res_file.body.header.signature in {b"BODY", b"PATH"} for res_file in self.content)

    def is_text_container(self) -> bool:
        return all(res_file.body.header.signature == b"CSTR" for res_file in self.content)
