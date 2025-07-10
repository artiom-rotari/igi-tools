import json
import subprocess
from io import BytesIO
from typing import ClassVar, Literal, Self
from zipfile import ZipFile

import typer
from pydantic import Field

from igipy.config import GameConfig
from igipy.formats import ilff, qsc


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
        content = self.content.removesuffix(b"\x00").decode("latin1")
        content = content.replace("\\", r"\\")
        content = content.replace(r'"', r"\"")
        content = "".join(character if ord(character) < 128 else f"\\x{ord(character):02X}" for character in content)
        return content


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

    @classmethod
    def cli_decode_all(cls, config: GameConfig, pattern: str = "**/*.res") -> None:
        for encoded_path in config.game_dir.glob(pattern):
            decoded_path = config.decoded_dir / encoded_path.relative_to(config.game_dir)
            decoded_path.parent.mkdir(parents=True, exist_ok=True)

            res_model = cls.model_validate_file(encoded_path)
            qsc_model = qsc.QSC(content=qsc.BlockStatement(statements=[]))
            qsc_model.content.statements.append(
                qsc.ExprStatement(
                    expression=qsc.Call(
                        function="BeginResource",
                        arguments=[
                            qsc.Literal(value=encoded_path.name),
                        ],
                    ),
                ),
            )

            for chunk_a, chunk_b in res_model.content_pairs:
                if isinstance(chunk_b, CSTRChunk):
                    qsc_model.content.statements.append(
                        qsc.ExprStatement(
                            expression=qsc.Call(
                                function="AddStringResource",
                                arguments=[
                                    qsc.Literal(value=chunk_a.get_cleaned_content()),
                                    qsc.Literal(value=chunk_b.get_cleaned_content()),
                                ],
                            ),
                        ),
                    )

                    continue

                if isinstance(chunk_b, BODYChunk):
                    content_path = decoded_path.with_suffix("") / chunk_a.get_cleaned_content().removeprefix("LOCAL:")
                    content_path.parent.mkdir(parents=True, exist_ok=True)
                    content_path.write_bytes(chunk_b.content)

                    qsc_model.content.statements.append(
                        qsc.ExprStatement(
                            expression=qsc.Call(
                                function="AddResource",
                                arguments=[
                                    qsc.Literal(value=content_path.absolute().as_posix()),
                                    qsc.Literal(value=chunk_a.get_cleaned_content()),
                                    qsc.Literal(value=chunk_b.header.alignment),
                                ],
                            ),
                        ),
                    )

                    continue

            if res_model.content_paths:
                qsc_model.content.statements.append(
                    qsc.ExprStatement(
                        expression=qsc.Call(
                            function="AddDirectoryResource",
                            arguments=[
                                qsc.Literal(value=res_model.content_paths[0].get_cleaned_content()),
                            ],
                        ),
                    )
                )

            qsc_model.content.statements.append(
                qsc.ExprStatement(
                    expression=qsc.Call(
                        function="EndResource",
                        arguments=[],
                    ),
                ),
            )

            decoded_path.with_suffix(".rsc").write_bytes(qsc_model.model_dump_stream()[0].getvalue())

            typer.secho(f'Decoded: "{encoded_path.as_posix()}"', fg=typer.colors.GREEN)
            typer.secho(f'To: "{decoded_path.as_posix()}"', fg=typer.colors.YELLOW)

    @classmethod
    def cli_encode_all(cls, config: GameConfig, pattern: str = "**/*.rsc", dry: bool = False) -> None:
        for decoded_path in config.decoded_dir.glob(pattern):
            encoded_path = config.encoded_dir / decoded_path.relative_to(config.decoded_dir)
            encoded_path.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                config.gconv_path.absolute().as_posix(),
                decoded_path.absolute().as_posix(),
                "-Verbosity=5",
            ]
            cwd = decoded_path.parent.absolute().as_posix()

            typer.secho(f'Going to execute: cd "{cwd}" && {" ".join(cmd)}', fg=typer.colors.GREEN)

            if not dry:
                result = subprocess.run(cmd, cwd=cwd, check=False)
