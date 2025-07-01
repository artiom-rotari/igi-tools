import struct
import wave
from io import BytesIO
from typing import Literal, Self

from pydantic import BaseModel, NonNegativeInt

from igipy.models import FileModel
from igipy.wav import adpcm


class WAV(FileModel):
    header: "WAVHeader"
    content: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO, path: str | None = None, size: int | None = None) -> Self:
        header = WAVHeader.model_validate_stream(stream)
        content = stream.read()
        return cls(meta_path=path, meta_size=size, header=header, content=content)

    @property
    def samples(self) -> bytes:
        if self.header.sound_pack in {0, 1}:
            return self.content
        if self.header.sound_pack in {2, 3}:
            return adpcm.decode(self.samples, channels=self.header.channels)

        raise ValueError(f"Unsupported sound pack: {self.header.sound_pack}")

    def to_wav(self, stream: BytesIO) -> BytesIO:
        samples = self.samples

        with wave.open(stream, "w") as wave_stream:
            wave_stream.setnchannels(self.header.channels)
            wave_stream.setsampwidth(self.header.sample_width // 8)
            wave_stream.setframerate(self.header.framerate)
            wave_stream.writeframesraw(samples)

        stream.seek(0)

        return stream


class WAVHeader(BaseModel):
    signature: Literal[b"ILSF"]
    sound_pack: Literal[0, 1, 2, 3]
    sample_width: Literal[16]
    channels: Literal[1, 2]
    unknown: NonNegativeInt
    framerate: Literal[11025, 22050, 44100]
    sample_count: NonNegativeInt

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        cls_struct = struct.Struct("4s4H2I")
        cls_fields = cls.__pydantic_fields__.keys()
        cls_values = cls_struct.unpack(stream.read(cls_struct.size))
        return cls(**dict(zip(cls_fields, cls_values, strict=True)))
