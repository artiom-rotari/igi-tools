from pathlib import Path
from typing import Self

from pydantic import Field
from pydantic_settings import BaseSettings
from rich import print

settings_file: Path = Path("igi.json")


class Settings(BaseSettings):
    game_dir: Path | None = Field(default=None, description="Directory where igi.exe is located")
    unpacked_dir: Path = Field(default="./unpacked", description="Directory where unpacked .res will be stored")
    converted_dir: Path = Field(default="./converted", description="Directory where converted files will be stored")

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
            print(
                f"Configuration file {settings_file.as_posix()} created in current directory with default values\n"
                f'Open it using any text editor and change value of "game_dir" to directory where igi.exe is.\n'
                f"After execute `igi config-check`"
            )

    def is_valid(self) -> bool:
        return all(
            [
                self.is_game_dir_configured(),
                self.is_unpacked_dir_configured(),
                self.is_converted_dir_configured(),
            ]
        )

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

    def is_unpacked_dir_configured(self) -> bool:
        check: bool = True

        if not self.unpacked_dir:
            print("unpacked_dir: is not set. Please set game dir in igi.json -> unpacked_dir")
            check = False
        elif not self.unpacked_dir.exists():
            self.unpacked_dir.mkdir(parents=True, exist_ok=True)
            check = True
        elif not self.unpacked_dir.is_dir():
            print(f"unpacked_dir: {self.unpacked_dir} is not a directory")
            check = False

        return check

    def is_converted_dir_configured(self) -> bool:
        check: bool = True

        if not self.converted_dir:
            print("converted_dir: is not set. Please set game dir in igi.json -> converted_dir")
            check = False
        elif not self.converted_dir.exists():
            self.converted_dir.mkdir(parents=True, exist_ok=True)
            check = True
        elif not self.converted_dir.is_dir():
            print(f"converted_dir: {self.converted_dir} is not a directory")
            check = False

        return check
