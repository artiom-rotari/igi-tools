from collections import defaultdict

from typer import Typer

from igi.config.cli import Settings

app = Typer(name="igi_game", add_completion=False)


@app.command()
def glob(pattern: str = "**/*.res"):
    settings: Settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    for i, file in enumerate(settings.game_dir.glob(pattern), start=1):
        print(f"[{i:>04}] {file.as_posix()}")


@app.command()
def extensions():
    settings: Settings = Settings.load()

    if not settings.is_game_dir_configured():
        return

    counter = defaultdict(lambda: 0)

    for file in settings.game_dir.glob("**/*"):
        counter[file.suffix] += 1

    for key, value in sorted(counter.items(), key=lambda item: item[1], reverse=True):
        print(f"{key}: {value}")
