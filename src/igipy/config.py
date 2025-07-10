from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, Field, PlainSerializer

JsonPrettyPath = Annotated[Path, PlainSerializer(lambda value: value.as_posix(), return_type=str, when_used="json")]


class GameConfig(BaseModel):
    game_dir: JsonPrettyPath = Path("C:/Games/ProjectIGI")
    work_dir: JsonPrettyPath = Path.cwd()

    @property
    def gconv(self) -> Path:
        return Path(__file__).parent / "bin" / "gconv.exe"

    @property
    def scripts_dir(self) -> Path:
        return self.work_dir / "scripts"

    @property
    def build_dir(self) -> Path:
        return self.work_dir / "build"

    @property
    def decoded_dir(self):
        return self.work_dir / "decoded"

    @property
    def extracted_dir(self):
        return self.work_dir / "extracted"


class Config(BaseModel):
    igi1: GameConfig = Field(default_factory=GameConfig)

    @classmethod
    def model_validate_file(cls, path: Path = None) -> Self:
        path = path or Path("igipy.json")

        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(cls.model_construct().model_dump_json(indent=2))

        if not path.is_file(follow_symlinks=False):
            raise FileNotFoundError(f"{path.as_posix()} isn't a file")

        return cls.model_validate_json(path.read_text())
