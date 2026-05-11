# flatsearch

[![Commit activity](https://img.shields.io/github/commit-activity/m/travisseymour/flatsearch)](https://img.shields.io/github/commit-activity/m/travisseymour/flatsearch)
[![License](https://img.shields.io/github/license/travisseymour/flatsearch)](https://img.shields.io/github/license/travisseymour/flatsearch)

A TUI tool for managing [Flatpak](https://flatpak.org/) applications. Search and install new apps, list and launch installed apps, or uninstall apps you no longer need. Use the arrow keys to navigate and press ENTER to act on your selection.

- **Github repository**: <https://github.com/travisseymour/flatsearch/>

## Usage

### Search and Install

```
flatsearch search [-y|--assumeyes] <search term>
```

Search for flatpak apps and optionally install a selected one.

```bash
flatsearch search comic
```

This will prompt you to verify before installing any app you choose.

```bash
flatsearch search -y comic
```

With `-y`, flatpak will start installing immediately without confirmation.

### List and Launch

```
flatsearch list [filter term]
```

Display installed flatpak apps. Select one to launch it.

```bash
flatsearch list
```

Shows all installed flatpak apps in a table. Select one to launch.

```bash
flatsearch list firefox
```

Filter the list to show only apps matching "firefox".

### Uninstall

```
flatsearch uninstall [-y|--assumeyes] [filter term]
```

Display installed flatpak apps and uninstall a selected one.

```bash
flatsearch uninstall
```

Shows all installed flatpak apps in a table. Select one to uninstall.

```bash
flatsearch uninstall firefox
```

Filter the list to show only apps matching "firefox".

```bash
flatsearch uninstall -y firefox
```

With `-y`, skip the confirmation prompt before uninstalling.

### Help

```bash
flatsearch --help           # Show all commands
flatsearch search --help    # Help for search command
flatsearch list --help      # Help for list command
flatsearch uninstall --help # Help for uninstall command
```

<mark>NOTICE:</mark> This tool has only tested on Linux Mint (Debian/Ubuntu base) with the flatpak tool installed.

## Installation

### Preparation

1. Make sure you have [uv (preferred)](https://docs.astral.sh/uv/) or [PipX](https://pipx.pypa.io/stable/) installed.

2. Make sure you have Python 3.10 or higher installed. If you need to install a version of Python, you can use `uv` to do this, for example:

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
