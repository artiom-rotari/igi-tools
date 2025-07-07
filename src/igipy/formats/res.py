import json
from io import BytesIO
from typing import ClassVar, Literal, Self
from zipfile import ZipFile

from pydantic import Field

from igipy.formats import ilff


class NAMEChunk(ilff.RawChunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"NAME")

    def get_cleaned_content(self) -> str:
        return self.content.removesuffix(b"\x00").decode("latin1")


class BODYChunk(ilff.RawChunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"BODY")


class CSTRChunk(ilff.RawChunk):
    @classmethod
    def model_validate_header(cls, header: ilff.ChunkHeader) -> None:
        ilff.model_validate_header(header, fourcc=b"CSTR")

    def get_cleaned_content(self) -> str:
        return self.content.removesuffix(b"\x00").decode("latin1")


class PATHChunk(ilff.RawChunk):
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
    content_pairs: list[tuple[NAMEChunk, BODYChunk]] | list[tuple[NAMEChunk, CSTRChunk]]
    content_paths: tuple[NAMEChunk, PATHChunk] | None = None

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header, content_type, chunks = super().model_validate_chunks(stream)

        if content_type != b"IRES":
            raise ValueError(f"Unknown content type: {content_type}")

        content_pairs = list(zip(chunks[::2], chunks[1::2], strict=True))
        content_paths = content_pairs.pop(-1) if content_pairs[-1][1].header.fourcc == b"PATH" else None

        # noinspection PyTypeChecker
        return cls(
            header=header,
            content_type=content_type,
            content_pairs=content_pairs,
            content_paths=content_paths,
        )

    def model_dump_stream(self) -> tuple[BytesIO, str]:
        stream = BytesIO()
        types = {chunk_b.header.fourcc for _, chunk_b in self.content_pairs}

        if types == {b"BODY"}:
            with ZipFile(stream, "w") as zip_stream:
                for chunk_a, chunk_b in self.content_pairs:
                    zip_stream.writestr(chunk_a.get_cleaned_content().removeprefix("LOCAL:"), chunk_b.content)

            return stream, ".zip"

        if types == {b"CSTR"}:
            content = [
                {
                    "key": chunk_a.get_cleaned_content().removeprefix("LOCAL:"),
                    "value": chunk_b.get_cleaned_content(),
                }
                for chunk_a, chunk_b in self.content_pairs
            ]

            stream.write(json.dumps(content, indent=4).encode())

            return stream, ".json"

        raise ValueError(f"Unknown file container type: {types}")
