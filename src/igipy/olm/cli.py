from collections import defaultdict

from polars import DataFrame
from rich import print  # noqa: A004
from typer import Typer

from igipy.config import Settings
from igipy.olm.models import OLM

app = Typer(add_completion=False, short_help="Submodule with OLM commands")


@app.command(short_help="For development purposes!!!")
def dev() -> tuple[DataFrame, DataFrame] | None:
    settings = Settings.load()

    if not settings.is_valid():
        print("Configuration file is not valid.")
        return None

    olm_headers = defaultdict(list)
    olm_item_headers = defaultdict(list)

    for src in settings.unpacked_dir.glob("**/*.olm"):
        try:
            olm = OLM.model_validate_file(src)

            for key, value in olm.header.model_dump().items():
                olm_headers[key].append(value)

            olm_headers["meta_size"].append(olm.meta_size)

            for item_header in olm.item_headers:
                for key, value in item_header.model_dump().items():
                    olm_item_headers[key].append(value)

        except ValueError:
            print(src.as_posix())
            raise

    df_headers = DataFrame(olm_headers)
    df_item_headers = DataFrame(olm_item_headers)

    return df_headers, df_item_headers
