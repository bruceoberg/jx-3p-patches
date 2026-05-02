# Installing jx3p on macOS

This guide will get the `jx3p` command installed on your Mac so you can convert JX-3P tape-dump WAV files to and from JSON or CSV. You only need the Terminal for two short steps; you do not need to know any programming.

## 1. Install `uv`

`uv` is a small tool that handles installing Python apps for you. Install it once with the official Mac installer.

1. Open the **Terminal** app (press ⌘-Space, type "Terminal", press Return).
2. Copy and paste this line into the Terminal, then press Return:

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. When it finishes, **quit the Terminal and open a new one**. This makes the new tool available.

## 2. Install `jx3p`

1. In the Finder, open the folder where you unzipped or downloaded the `jx-3p-patches` project. You should see folders named `jx3p`, `schemas`, `docs`, and a file called `pyproject.toml`.
2. In the Terminal, type `cd ` (with a trailing space — note the space), then drag the project folder from the Finder onto the Terminal window. The full path will appear. Press Return.
3. Run:

   ```sh
   uv tool install .
   ```

   This installs `jx3p` and adds it to your `PATH` so you can run it from anywhere.

To check it worked, run:

```sh
jx3p --help
```

You should see a list of commands.

## 3. Using `jx3p`

Once installed, you can use `jx3p` from any folder. The four main commands are:

| Goal                                            | Command                                          |
| ----------------------------------------------- | ------------------------------------------------ |
| Decode a tape-dump recording into JSON          | `jx3p wav-to-json mydump.wav patches.json`       |
| Encode a JSON patch bank back into a WAV        | `jx3p json-to-wav patches.json mydump.wav`       |
| Convert an existing CSV bank to JSON            | `jx3p csv-to-json patches.csv patches.json`      |
| Convert a JSON bank to CSV                      | `jx3p json-to-csv patches.json patches.csv`      |

Tip: the same drag-and-drop trick works for the input files. Type the command up to the first filename, then drag the file from the Finder onto the Terminal window to fill in the full path.

## Updating

When a new version comes out, download the new project folder, open Terminal in it the same way as above, and run:

```sh
uv tool install . --reinstall
```

## Uninstalling

```sh
uv tool uninstall jx3p
```
