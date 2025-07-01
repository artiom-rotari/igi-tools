from io import BytesIO
from struct import Struct
from typing import ClassVar, Literal, Self
from zipfile import ZipFile

from pydantic import BaseModel, Field, NonNegativeInt

from igipy.models import FileModel, StructModel


def align(stream: BytesIO, padding: int) -> None:
    padding_length = (padding - stream.tell() % padding) % padding
    padding_data = stream.read(padding_length)

    if padding_data != b"\x00" * padding_length:
        message = f"Expected padding data to be null bytes: {padding_data}"
        raise ValueError(message)


class ChunkHeader(StructModel):
    _struct: ClassVar[Struct] = Struct("4s3I")

    signature: bytes = Field(min_length=4, max_length=4)
    length: NonNegativeInt
    padding: Literal[4, 32]
    next_position: NonNegativeInt


class Chunk(BaseModel):
    header: ChunkHeader
    content: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        # noinspection PyTypeChecker
        header_class: ChunkHeader = cls.__pydantic_fields__["header"].annotation
        header = header_class.model_validate_stream(stream)

        align(stream, header.padding)

        content = stream.read(header.length)
        return cls(header=header, content=content)


class ChunkPair(BaseModel):
    chunk_a: Chunk
    chunk_b: Chunk

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        # noinspection PyTypeChecker
        chunk_a_class: Chunk = cls.__pydantic_fields__["chunk_a"].annotation
        # noinspection PyTypeChecker
        chunk_b_class: Chunk = cls.__pydantic_fields__["chunk_b"].annotation

        chunks = []

        for chunk_class in (chunk_a_class, chunk_b_class):
            position = stream.tell()
            chunk = chunk_class.model_validate_stream(stream)
            chunks.append(chunk)
            stream.seek(position + chunk.header.next_position)

        return cls(**dict(zip(("chunk_a", "chunk_b"), chunks, strict=True)))


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
        raise ValueError(f"Unsupported chunk signature: {self.header.signature}")


class RESHeader(StructModel):
    _struct: ClassVar[Struct] = Struct("4s3I4s")

    signature: Literal[b"ILFF"]
    length: NonNegativeInt
    padding: Literal[4, 32]
    next_position: NonNegativeInt
    content_signature: Literal[b"IRES"]


class RESFile(ChunkPair):
    chunk_a: RESChunkNAME
    chunk_b: RESChunkBODY

    def is_file(self) -> bool:
        return self.chunk_b.header.signature == b"BODY"

    def is_text(self) -> bool:
        return self.chunk_b.header.signature == b"CSTR"

    def is_path(self) -> bool:
        return self.chunk_b.header.signature == b"PATH"

    @property
    def file_name(self) -> str:
        if not self.is_file():
            raise ValueError(f"Is not a file: {self.name.get_cleaned_content()}")
        return self.chunk_a.get_cleaned_content().removeprefix("LOCAL:")

    @property
    def file_content(self) -> bytes | str:
        if not self.is_file():
            raise ValueError(f"Is not a file: {self.name.get_cleaned_content()}")
        return self.chunk_b.get_cleaned_content()


class RES(FileModel):
    header: RESHeader
    content: list[RESFile]

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, path: str | None = None, size: int | None = None) -> Self:
        header = RESHeader.model_validate_stream(stream)

        align(stream, header.padding)

        content = []

        while True:
            res_file = RESFile.model_validate_stream(stream)

            content.append(res_file)

            if res_file.chunk_b.header.next_position == 0:
                break

        return cls(meta_path=path, meta_size=size, header=header, content=content)

    def is_file_container(self) -> bool:
        return all(res_file.chunk_b.header.signature in {b"BODY", b"PATH"} for res_file in self.content)

    def is_text_container(self) -> bool:
        return all(res_file.chunk_b.header.signature == b"CSTR" for res_file in self.content)

    def to_zip(self, stream: BytesIO | None = None) -> BytesIO:
        if not self.is_file_container():
            raise ValueError("Current is not a file container")

        stream = stream or BytesIO()

        with ZipFile(stream, "w") as zip_stream:
            for res_file in self.content:
                if res_file.is_file():
                    zip_stream.writestr(res_file.file_name, res_file.file_content)

        stream.seek(0)

        return stream
