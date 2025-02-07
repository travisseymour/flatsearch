# flatsearch

[![Commit activity](https://img.shields.io/github/commit-activity/m/travisseymour/flatsearch)](https://img.shields.io/github/commit-activity/m/travisseymour/flatsearch)
[![License](https://img.shields.io/github/license/travisseymour/flatsearch)](https://img.shields.io/github/license/travisseymour/flatsearch)

This tool uses the Textual framework to display a scrollable table of search results from [flatpak](https://flatpak.org/). Use the arrow keys to select an entry and press ENTER to be prompted for installation.

- **Github repository**: <https://github.com/travisseymour/flatsearch/>

## Usage

```bash
flatsearch comic
```

<mark>NOTICE:</mark> This tool has only tested on Linux (Debian-type, Pop_OS! in particular) with the flatpak tool installed.

![asciinema cast of flatsearch usage](media/flatsearch.svg)
(https://asciinema.org/a/A3FPc7QbYHjRoOk20GJVYbiPR)

## Installation

### Preparation

1. Make sure you have [uv (preferred)](https://docs.astral.sh/uv/) or [PipX](https://pipx.pypa.io/stable/) installed.

2. Make sure you have Python 3.9 or higher installed. If you need to install a version of Python, you can use `uv` to do this, for example:

    To check to see which versions of Python you already have

    ```bash
   uv python list
    ```

    To install Python 3.11

    ```bash
    uv python install 3.11
    ```

### Installation


```bash
uv tool install git+https://github.com/travisseymour/flatsearch.git
```

or

```bash
pipx install git+https://github.com/travisseymour/flatsearch.git
```

### Upgrade

```bash
uv tool upgrade flatsearch
```

or

```bash
pipx upgrade flatsearch
```

### Removal

```bash
uv tool uninstall flatsearch
```

or 

```bash
pipx uninstall flatsearch
```



