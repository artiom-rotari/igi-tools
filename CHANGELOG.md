
# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.1] - 2025-06-28

This is the first release

### Added

- `.res` unpacker (only `.res` files that contain files)
- `.qvm` convert to `.qsc`
- `.wav` convert to `.wav` (waveform) with decoding or `ADPCM` encoded sound files.

## [0.1.2] - 2025-06-29

Prepare the repository for publication

### Fixed

- `python -m igipy version` returns an error

## [0.1.3] - 2025-06-30

Minor fixes

### Fixed

- Fixed script name in `pyproject.toml`
- Bump up `pydantic-settings` version
- Code clean


## [0.2.0] - 2025-07-04

Refactor package organization and add .tex support.

### Added
- Convert .tex, .spr, .pic to .tga
- Convert text .res to .json
- Convert file .res to .zip instead directory

### Changed
- Removed `igipy version` command and added `igipy --version` flag.
- Config file renamed from `igi.json` into `igipy.json`
- Removed `igipy config-initialize` and `igipy config-check` if favor of `igipy --config`
- Removed `igipy res unpack` and `igipy res unpack-all` if favor of `igipy res convert-all`
- Removed `igipy qvm convert`
- Removed `igipy wav convert`
