from pathlib import Path
from typing import Self

from pydantic_settings import BaseSettings

settings_file: Path = Path("igi.json")


class Settings(BaseSettings):
    game_dir: Path | None = None
    work_dir: Path | None = Path()

    @classmethod
    def load(cls) -> Self:
        with settings_file.open() as fp:
            return cls.model_validate_json(fp.read())

    @classmethod
    def dump(cls) -> None:
        if settings_file.exists():
            print("Settings file already exists")
            return

        with settings_file.open("w") as fp:
            print(cls().model_dump_json(indent=2), file=fp)
            print("File created")

    def check(self):
        if all(
            [
                self.is_game_dir_configured(),
                self.is_work_dir_configured(),
            ]
        ):
            print("Settings seems to be ok")

    def is_game_dir_configured(self) -> bool:
        check: bool = True

        if not self.game_dir:
            print("game_dir: is not set. Please set game dir in igi.json -> game_dir")
            check = False
        elif not self.game_dir.exists():
            print(f"game_dir: {self.game_dir} does not exist")
            check = False
        elif not self.game_dir.is_dir():
            print(f"game_dir {self.game_dir} is not a directory")
            check = False
        elif not self.game_dir.joinpath("igi.exe").is_file():
            print(f"game_dir: {self.game_dir} must point to directory that contain igi.exe")
            check = False

        return check

    def is_work_dir_configured(self) -> bool:
        check: bool = True

        if not self.work_dir:
            print("work_dir: is not set. Please set game dir in igi.json -> work_dir")
            check = False
        if not self.work_dir.exists():
            print(f"work_dir: {self.work_dir} does not exist")
            check = False
        if not self.work_dir.is_dir():
            print(f"work_dir: {self.work_dir} is not a directory")
            check = False

        return check
