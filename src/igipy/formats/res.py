import subprocess
from io import BytesIO
from typing import ClassVar, Literal, Self

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

    @classmethod
    def cli_decode_all(cls, config: GameConfig, pattern: str = "**/*.res") -> None:
        for res_path in config.game_dir.glob(pattern):
            dst_path = config.res_extract_dir / res_path.relative_to(config.game_dir).with_suffix("")
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            res_model = cls.model_validate_file(res_path)
            qsc_model = qsc.QSC(content=qsc.BlockStatement(statements=[]))
            qsc_model.content.statements.append(
                qsc.ExprStatement(
                    expression=qsc.Call(
                        function="BeginResource",
                        arguments=[
                            qsc.Literal(value=res_path.name),
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
                    content_name = chunk_a.get_cleaned_content().removeprefix("LOCAL:")
                    content_path = dst_path.joinpath(content_name).relative_to(dst_path.parent)
                    content_path.parent.mkdir(parents=True, exist_ok=True)
                    content_path.write_bytes(chunk_b.content)

                    qsc_model.content.statements.append(
                        qsc.ExprStatement(
                            expression=qsc.Call(
                                function="AddResource",
                                arguments=[
                                    qsc.Literal(value=content_path.as_posix()),
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

            rsc_path = dst_path.with_suffix(".rsc")
            rsc_path.write_bytes(qsc_model.model_dump_stream()[0].getvalue())

            typer.secho(f'Decoded: "{res_path.as_posix()}"', fg=typer.colors.GREEN)
            typer.secho(f'To: "{rsc_path.as_posix()}"', fg=typer.colors.YELLOW)

    @classmethod
    def cli_encode_all(cls, config: GameConfig, pattern: str = "**/*.rsc") -> None:
        for rsc_path in config.res_extract_dir.glob(pattern):
            subprocess.run(
                [config.gconv.absolute().as_posix(), rsc_path.name, "-Verbosity=5"],
                cwd=rsc_path.parent.absolute().as_posix(),
                check=False,
            )

            res_src_path = rsc_path.with_suffix(".res")
            res_dst_path = config.build_dir / rsc_path.relative_to(config.res_extract_dir).with_suffix(".res")

            if res_src_path.is_file(follow_symlinks=False):
                res_dst_path.parent.mkdir(parents=True, exist_ok=True)
                res_src_path.replace(res_dst_path)
