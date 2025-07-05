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

   You should see output like `Version: 0.2.1` or higher.

3. To see available modules:

   ```bash
   python -m igipy --help
   ```

4. Generate the configuration file:

   ```bash
   python -m igipy
   ```

   This will create `igipy.json` in the current directory. Open it and set the `"source_dir"` to your IGI 1 installation path, for example:

   ```json
   {
     "igi1": {
       "source_dir": "C:/Games/ProjectIGI",
       "unpack_dir": "./unpack",
       "target_dir": "./target"
     }
   }
   ```

5. Verify configuration:

   ```bash
   python -m igipy
   ```

   If everything is configured correctly, you should see no warnings below the help message.

## User Guide

### Extract IGI 1 `.res` Files

```bash
python -m igipy igi1 convert-all-res
```

* Converts archive `.res` files to `.zip` (in `unpack_dir`)
* Converts text `.res` files to `.json` (in `target_dir`)

### Convert IGI 1 `.wav` Files

```bash
python -m igipy igi1 convert-all-wav
```

Converts all `.wav` files (from `source_dir` and `.zip` archives) to standard `.wav` in `target_dir`.

### Convert IGI 1 `.qvm` Files

```bash
python -m igipy igi1 convert-all-qvm
```

Converts `.qvm` files in `source_dir` to `.qsc` format in `target_dir`.

### Convert IGI 1 `.tex`, `.spr`, and `.pic` Files

```bash
python -m igipy igi1 convert-all-tex
```

Converts `.tex`, `.spr`, and `.pic` files (from `source_dir` and archives) to `.tga` in `target_dir`.

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
