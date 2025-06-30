import struct
import wave
from io import BytesIO
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, NonNegativeInt

from . import adpcm


class WAVHeader(BaseModel):
    signature: Literal[b"ILSF"]
    sound_pack: Literal[0, 1, 2, 3]
    sample_width: Literal[16]
    channels: Literal[1, 2]
    unknown: NonNegativeInt
    sample_rate: Literal[11025, 22050, 44100]
    sample_count: NonNegativeInt

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        # noinspection PyTypeChecker
        data = struct.unpack("4s4H2I", stream.read(20))
        return cls(
            signature=data[0],
            sound_pack=data[1],
            sample_width=data[2],
            channels=data[3],
            unknown=data[4],
            sample_rate=data[5],
            sample_count=data[6],
        )


class WAV(BaseModel):
    header: WAVHeader
    samples: bytes

    @classmethod
    def model_validate_file(cls, path: Path | str) -> Self:
        # noinspection PyTypeChecker
        return cls.model_validate_stream(BytesIO(Path(path).read_bytes()))

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header = WAVHeader.model_validate_stream(stream)
        samples = stream.read()
        return cls(header=header, samples=samples)

    def model_dump_stream(self, stream: BytesIO) -> BytesIO:
        with wave.open(stream, "w") as wave_stream:
            wave_stream.setnchannels(self.header.channels)
            wave_stream.setsampwidth(self.header.sample_width // 8)
            wave_stream.setframerate(self.header.sample_rate)

            if self.header.sound_pack in {0, 1}:
                wave_stream.writeframesraw(self.samples)
            elif self.header.sound_pack in {2, 3}:
                wave_stream.writeframesraw(adpcm.decode(self.samples, channels=self.header.channels))
            else:
                message = f"Unsupported sound pack: {self.header.sound_pack}"
                raise ValueError(message)

        stream.seek(0)

        return stream
