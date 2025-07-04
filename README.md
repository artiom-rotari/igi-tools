# IGI Tools

**igipy** is a Python CLI tool for converting game files from *Project I.G.I: I'm Going In* (IGI 1) into standard, widely supported formats. It is a direct successor and refactor of the tool published at [https://github.com/NEWME0/Project-IGI/](https://github.com/NEWME0/Project-IGI/).

## Features

* Convert `.res` files to `.zip` or `.json` (depending on whether it's an archive or translation file)
* Convert `.qvm` files to `.qsc`
* Convert `.wav` files to standard Waveform `.wav` including ADPCM-encoded sound files.
* Convert `.tex`, `.spr`, and `.pic` files to `.tga`

## Installation

Requires **Python 3.13**.

To install:

```bash
python -m pip install --upgrade igipy
```

## Quickstart

1. Create a folder where you want to extract or convert game files.

2. Open PowerShell (or terminal) and verify the installation:

   ```bash
   python -m igipy --version
   ```

   You should see output like `Version: 0.2.0` or higher.

3. To see available modules:

   ```bash
   python -m igipy --help
   ```

4. Generate the configuration file:

   ```bash
   python -m igipy --config
   ```

   This will create `igipy.json` in the current directory. Open it and set the `"game_dir"` to your IGI 1 installation path, for example:

   ```json
   {
     "game_dir": "C:/Users/artiom.rotari/Desktop/ProjectIGI",
     "archive_dir": "./archive",
     "convert_dir": "./convert"
   }
   ```

5. Verify configuration:

   ```bash
   python -m igipy --config
   ```

   If everything is configured correctly, you should see no warnings below the settings output.

## User Guide

### Extract `.res` Archives

```bash
python -m igipy res convert-all
```

* Converts archive `.res` files to `.zip` (in `archive_dir`)
* Converts text `.res` files to `.json` (in `convert_dir`)

### Convert `.wav` Files

```bash
python -m igipy wav convert-all
```

Converts all `.wav` files (from `game_dir` and `.zip` archives) to standard `.wav` in `convert_dir`.

### Convert `.qvm` Files

```bash
python -m igipy qvm convert-all
```

Converts `.qvm` files in `game_dir` to `.qsc` format in `convert_dir`.

### Convert `.tex`, `.spr`, and `.pic` Files

```bash
python -m igipy tex convert-all
```

Converts `.tex`, `.spr`, and `.pic` files (from `game_dir` and archives) to `.tga` in `convert_dir`.

## Supported Game File Formats

Below is a summary of the file formats in *Project I.G.I*, including their locations and conversion support:

| Extension      | In Game Dir | In `.res` | Convertible     |
|----------------|-------------|-----------|-----------------|
| `.olm`         | -           | 25,337    | ❌ No            |
| `.tex`         | 26          | 7,199     | ✅ Yes           |
| `.mef`         | -           | 6,794     | ❌ No            |
| `.qvm`         | 997         | -         | ✅ Yes           |
| `.wav`         | 394         | 346       | ✅ Yes           |
| `.dat` (graph) | 300         | -         | ❌ No            |
| `.spr`         | -           | 158       | ✅ Yes           |
| `.res`         | 92          | -         | ✅ Yes           |
| `.dat` (mtp)   | 17          | -         | ❌ No            |
| `.mtp`         | 17          | -         | ❌ No            |
| `.bit`         | 14          | -         | ❌ No            |
| `.cmd`         | 14          | -         | ❌ No            |
| `.ctr`         | 14          | -         | ❌ No            |
| `.lmp`         | 14          | -         | ❌ No            |
| `.fnt`         | 2           | 9         | ❌ No            |
| `.hmp`         | 6           | -         | ❌ No            |
| `.rtf`         | 6           | -         | ⚠️ Regular file |
| `.txt`         | 6           | -         | ⚠️ Regular file |
| `.iff`         | 6           | -         | ❌ No            |
| `.pic`         | -           | 5         | ✅ Yes           |
| `.url`         | 5           | -         | ⚠️ Regular file |
| `.avi`         | 5           | -         | ⚠️ Regular file |
| `.AFP`         | 3           | -         | ⚠️ Regular file |
| `.exe`         | 2           | -         | ⚠️ Regular file |
