from collections import defaultdict
from typing import Any

from polars import DataFrame
from rich import print  # noqa: A004
from typer import Typer

from igipy.config import Settings
from igipy.olm.models import OLM

app = Typer(add_completion=False, short_help="Submodule with OLM commands")


@app.command(short_help="For development purposes!!!")
def dev() -> Any:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return None

    olm_headers = defaultdict(list)

    for src in settings.unpacked_dir.glob("**/*.olm"):
        try:
            olm = OLM.model_validate_file(src)

            for key, value in olm.header.model_dump().items():
                olm_headers[key].append(value)

            olm_headers["content_size"].append(len(olm.content))

        except ValueError:
            print(src.as_posix())

    return DataFrame(olm_headers)
