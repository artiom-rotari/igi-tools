import typer

from igipy import formats

igi1_app = typer.Typer(add_completion=False)


@igi1_app.callback(invoke_without_command=True)
def igi1_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@igi1_app.command(short_help="Extract all .res files found in `{{game_dir}}`")
def decode_all_res(ctx: typer.Context, pattern: str = "**/*.res") -> None:
    formats.RES.cli_decode_all(config=ctx.obj.igi1, pattern=pattern)


@igi1_app.command(short_help="Execute script `{{scripts_dir}}/encode-all-res.qsc`")
def encode_all_res(ctx: typer.Context) -> None:
    formats.RES.cli_encode_all(config=ctx.obj.igi1)


@igi1_app.command(short_help="Decode all .wav files found in `{{game_dir}} and {{work_dir}}/extracted`")
def decode_all_wav(ctx: typer.Context, pattern: str = "**/*.wav") -> None:
    formats.WAV.cli_decode_all(config=ctx.obj.igi1, pattern=pattern)


@igi1_app.command(short_help="Execute script `{{scripts_dir}}/encode-all-wav.qsc`")
def encode_all_wav(ctx: typer.Context) -> None:
    formats.WAV.cli_encode_all(config=ctx.obj.igi1)
