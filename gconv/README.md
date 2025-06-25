# `gconv.exe`

Is a tool delivered with "I.G.I.-2: Covert Strike" game. This tool has three files:

- `gconv.exe`
- `gconvapi.dll`
- `vqdll.dll`

It can be used to convert regular file formats into game formats. Accepts as argument an `.qsc` script with instructions to execute.

## Usage example

We have a script `gconv/example_01.qsc` with content like:

```
ConvertSoundFile("example_01/m1_ambience_regular.wav", "example_01/m1_ambience_encoded.wav", 0);
```

Execution of this script will convert file `gconv/example_01/m1_ambience_regular.wav` into internal format and will save it as `gconv/example_01/m1_ambience_encoded.wav`.

To execute this script we have to open `gconv` folder in PowerShell terminal and execute

```shell
.\gconv.exe example_01.qsc
```
