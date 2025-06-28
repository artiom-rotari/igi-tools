# IGI Tools

**igipy** is a CLI application built on top of python for converting game files from `Project I.G.I: I'm going in` (or simple - IGI 1) formats into standard (common used) formats.

## Features

- Extract files from `.res` archives
- Decompile `.qvm` files
- Convert `.wav` into regular Waveform. Including ADPCM encoded files.


## Installation

This package requires `python 3.13` (at least it is developed and tested on this python version).

To install the package itself, run:

```
python -m pip install --upgrade igipy
```

## Quickstart

Create somewhere on your PC a folder where you want to extract game files. Open PowerShell and run:

```
python -m igipy version
```

You should see `Version: 0.1.2` (or higher). That means that the package is installed correctly.

To see all available modules, run:

```
python -m igipy --help
```

To execute one or another conversion command, this package requires a minimal configuration. Run:

```
python -m igipy config-initialize
```

This command will create in the current directory a file - `igi.json`. Open this file with your favorite text editor and update value of `"game_dir"` from `none` to a path where IGI 1 is installed. For example:

```
{
  "game_dir": "C:/Users/artiom.rotari/Desktop/ProjectIGI",
  "unpacked_dir": "unpacked",
  "converted_dir": "converted"
}
```

Other settings you can leave as is for now.

To check the configuration, execute:

```
python -m igipy config-check
```

If everything is good you must see: `Configuration file is valid`. If not, then please fix all issues in the config file and try again.


## User guide

### Extract `.res` archives

```
python -m igipy res unpack-all
```

This command will iterate all `.res` files in game directory and will unpack them into `./unpacked` directory with respecting the game folder structure.

### Convert `.wav` files

```
python -m igipy wav convert-all
```

This command will iterate all `.wav` files from game folder and `./unpacked` folder and will convert them into `./converted` folder with respecting the game folder structure.

### Convert `.qvm` files

```
python -m igipy qvm convert-all
```

This command will iterate all `.qvm` files from game folder and will convert them into `.qsc` in the `./converted` folder.
