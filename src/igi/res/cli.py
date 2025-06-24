import struct
from io import BytesIO
from pathlib import Path
from typing import Literal, Self
from zipfile import ZIP_STORED, ZipFile

from pydantic import BaseModel, Field, NonNegativeInt
from typer import Typer

from igi.config import Settings

app = Typer(name="igi_res")


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


class RES(BaseModel):
    header: RESHeader
    content: list[tuple[RESChunkNAME, RESChunkBODY]]

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

            content.append((name_chunk, body_chunk))

            if body_chunk.header.next_position == 0:
                break

        return cls(header=header, content=content)

    def is_archive(self) -> bool:
        return all(body_chunk.header.signature in {b"BODY", b"PATH"} for _, body_chunk in self.content)


@app.command()
def inspect(src: Path) -> None:
    res = RES.model_validate_file(src)

    for name_chunk, body_chunk in res.content:
        filename = name_chunk.get_cleaned_content().removeprefix("LOCAL:")
        content = body_chunk.get_cleaned_content()
        print(filename, len(content))


@app.command(short_help="Convert .res file to .zip file")
def convert(src: Path, dst: Path) -> None:
    if not src.exists() and src.is_file():
        print(f"{src} is not a file.")
        return

    if dst.exists():
        print(f"{dst} already exists.")
        return

    res = RES.model_validate_file(src)

    if not res.is_archive():
        print(f"{src} is not a archive.")
        return

    dst_file = BytesIO()
    with ZipFile(dst_file, "w", compression=ZIP_STORED) as zip_file:
        for name_chunk, body_chunk in res.content:
            if body_chunk.header.signature == b"PATH":
                continue

            filename = name_chunk.get_cleaned_content().removeprefix("LOCAL:")
            content = body_chunk.get_cleaned_content()
            zip_file.writestr(filename, content)

    dst_file.seek(0)
    dst_data = dst_file.read()

    # noinspection PyTypeChecker
    dst.write_bytes(dst_data)


@app.command(short_help="Convert all .res files found in game_dir to .zip")
def convert_all() -> None:
    settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    if not settings.is_work_dir_configured():
        return

    for src_filepath in settings.game_dir.glob("**/*.res"):
        dst_filepath = settings.work_dir.joinpath(src_filepath.relative_to(settings.game_dir)).with_suffix(".zip")
        dst_filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            convert(src_filepath, dst_filepath)
        except Exception as e:
            print(src_filepath)
            print(e)
