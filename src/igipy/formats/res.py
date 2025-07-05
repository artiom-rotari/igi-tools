import json
from io import BytesIO
from pathlib import Path
from typing import ClassVar, Literal
from zipfile import ZipFile

from pydantic import Field, field_validator

from igipy.formats import ilff


class NAMEChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"NAME")

    def get_cleaned_content(self) -> str:
        return self.content.removesuffix(b"\x00").decode("latin1")


class BODYChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"BODY")


class CSTRChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"CSTR")

    def get_cleaned_content(self) -> str:
        return self.content.removesuffix(b"\x00").decode("latin1")


class PATHChunk(ilff.Chunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"PATH")

    def get_cleaned_content(self) -> str:
        return self.content.removesuffix(b"\x00").decode("latin1")


class RES(ilff.ILFF):
    chunk_mapping: ClassVar[dict[bytes, type[ilff.Chunk]]] = {
        b"NAME": NAMEChunk,
        b"BODY": BODYChunk,
        b"CSTR": CSTRChunk,
        b"PATH": PATHChunk,
    }

    content_type: Literal[b"IRES"] = Field(description="Content type")
    content: list[NAMEChunk | BODYChunk | CSTRChunk | PATHChunk]

    # noinspection PyNestedDecorators
    @field_validator("content", mode="after")
    @classmethod
    def validate_content(cls, value: list[ilff.Chunk]) -> list[ilff.Chunk]:
        if len(value) % 2 != 0:
            raise ValueError("Content length is not even")

        for chunk_a, chunk_b in zip(value[::2], value[1::2], strict=True):
            if chunk_a.header.fourcc != b"NAME":
                raise ValueError("Expected NAME chunk before BODY/CSTR/PATH chunk")

            if chunk_b.header.fourcc not in {b"BODY", b"CSTR", b"PATH"}:
                raise ValueError("Expected BODY/CSTR/PATH chunk after NAME chunk")

        return value

    def model_dump_stream(self, path: Path, stream: BytesIO) -> tuple[Path, BytesIO]:
        pairs = list(zip(self.content[::2], self.content[1::2], strict=False))

        if pairs[-1][1].header.fourcc == b"PATH":
            pairs = pairs[:-1]

        types = set(chunk_b.header.fourcc for _, chunk_b in pairs)

        if types == {b"BODY"}:
            path = path.with_suffix(".zip")

            with ZipFile(stream, "w") as zip_stream:
                for chunk_a, chunk_b in pairs:
                    zip_stream.writestr(chunk_a.get_cleaned_content(), chunk_b.content)

            return path, stream

        if types == {b"CSTR"}:
            path = path.with_suffix(".json")

            content = [
                {
                    "key": chunk_a.get_cleaned_content(),
                    "value": chunk_b.get_cleaned_content(),
                }
                for chunk_a, chunk_b in pairs
            ]

            stream.write(json.dumps(content, indent=4).encode())

            return path, stream

        raise ValueError(f"Unknown file container type: {types}")
