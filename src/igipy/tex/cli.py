from collections import defaultdict
from itertools import chain

import polars as pl
from rich import print  # noqa: A004
from typer import Typer

from igipy.config import Settings
from igipy.tex.models import TEX

app = Typer(add_completion=False, short_help="Submodule with TEX commands")


@app.command(short_help="List .tex")
def dev() -> pl.DataFrame | None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return None

    content = defaultdict(list)

    for directory in [settings.game_dir, settings.unpacked_dir]:
        for src in chain(
            directory.glob("**/*.tex"),
            directory.glob("**/*.spr"),
            directory.glob("**/*.pic"),
        ):
            print(src)
            tex = TEX.model_validate_file(src)

            for mipmap in tex.mipmaps:
                content["level"].append(mipmap.header.level)
                content["mode"].append(mipmap.header.mode)
                content["width"].append(mipmap.header.bitmap_width)
                content["height"].append(mipmap.header.bitmap_height)

    return pl.DataFrame(content)
