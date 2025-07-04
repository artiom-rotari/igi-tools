# IGI Tools

**igipy** is a CLI application built on top of python for converting game files from `Project I.G.I: I'm going in` (or simple - IGI 1) formats into standard (common used) formats.

## Features

- Convert `.res` files to `.zip` or `.json` (depending on is archive or translation file)
- Convert `.qvm` files to `.qsc`
- Convert `.wav` into regular Waveform `.wav`. Decode `ADPCM` encoded files.
- Convert `.tex`, `.spr` and `.pic` into `.tga`

## Installation

This package requires `python 3.13`.

To install the package itself, run:

```
python -m pip install --upgrade igipy
```

## Quickstart

Create somewhere on your PC a folder where you want to extract game files. Open PowerShell and run:

```
python -m igipy --version
```

You should see `Version: 0.2.0` (or higher). That means that the package is installed correctly.

To see all available modules, run:

```
python -m igipy --help
```

To execute one or another conversion command, this package requires a minimal configuration. Run:

```
python -m igipy --config
```

This command will create in the current directory a file - `igipy.json`. Open this file with your favorite text editor and update value of `"game_dir"` to a path where IGI 1 is installed. For example:

```
{
  "game_dir": "C:/Users/artiom.rotari/Desktop/ProjectIGI",
  "archive_dir": "./archive",
  "convert_dir": "./convert"
}
```

Other settings you can leave as is for now.

To check the configuration, execute:

```
python -m igipy --config
```

If everything is good, you must see no warning bellow settings dump.


## User guide

### Extract `.res` archives

```
python -m igipy res convert-all
```

This command will iterate all `.res` files in game directory and will:
- convert into `.zip` in `archive_dir` if it is a container of files
- convert into `.json` in `convert_dir` if it is a container of a text

### Convert `.wav` files

```
python -m igipy wav convert-all
```

This command will iterate all `.wav` files in `game_dir` and `archive_dir` zips and will convert them into regular `.wav` in `convert_dir`.

### Convert `.qvm` files

```
python -m igipy qvm convert-all
```

This command will iterate all `.qvm` files in `game_dir` and will convert them into `.qsc` in the `convert_dir`.

### Convert `.tex`, `.spc` or `.pic` files

```
python -m igipy tex convert-all
```

This command will iterate all `.tex`, `.spc` or `.pic` files in `game_dir` and `archive_dir` zips and will convert them into `.tga` in `convert_dir`.


## Game file formats

Game directory of "Project I.G.I: I'm going in" contains the following extensions:

| Extension      | In game directory | In .res files | Can convert |
|----------------|-------------------|---------------|-------------|
| `.olm`         | -                 | 25337         | -           |
| `.tex`         | 26                | 7199          | Yes         |
| `.mef`         | -                 | 6794          | -           |
| `.qvm`         | 997               | -             | Yes         |
| `.wav`         | 394               | 346           | Yes         |
| `.dat` (graph) | 300               | -             | -           |
| `.spr`         | -                 | 158           | Yes         |
| `.res`         | 92                | -             | Yes         |
| `.dat` (mtp)   | 17                | -             | -           |
| `.mtp`         | 17                | -             | -           |
| `.bit`         | 14                | -             | -           |
| `.cmd`         | 14                | -             | -           |
| `.ctr`         | 14                | -             | -           |
| `.lmp`         | 14                | -             | -           |
| `.fnt`         | 2                 | 9             | -           |
| `.hmp`         | 6                 | -             | -           |
| `.rtf`         | 6                 | -             | Is regular  |
| `.txt`         | 6                 | -             | Is regular  |
| `.iff`         | 6                 | -             | -           |
| `.pic`         | -                 | 5             | Yes         |
| `.url`         | 5                 | -             | Is regular  |
| `.avi`         | 5                 | -             | Is regular  |
| `.AFP`         | 3                 | -             | Is regular  |
| `.exe`         | 2                 | -             | Is regular  |
