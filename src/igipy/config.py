from pathlib import Path
from typing import ClassVar, Self

from pydantic import BaseModel, Field

from igipy.managers import IGI1Manager


class Config(BaseModel):
    path: ClassVar[Path] = Path("igipy.json")
    igi1: IGI1Manager = Field(default_factory=IGI1Manager)

    @classmethod
    def model_validate_file(cls) -> Self:
        if not cls.path.exists():
            cls.path.parent.mkdir(parents=True, exist_ok=True)
            cls.path.write_text(cls.model_construct().model_dump_json(indent=2))

        if not cls.path.is_file(follow_symlinks=False):
            raise FileNotFoundError(f"{cls.path.as_posix()} isn't a file")

        return cls.model_validate_json(cls.path.read_text())
