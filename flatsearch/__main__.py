#!/usr/bin/env python3
"""
FlatSearch. This tool uses the Textual framework to display a scrollable
table of search results from [flatpak](https://flatpak.org/).
Use the arrow keys to select an entry and press ENTER to be prompted for installation.

Copyright (C) 2024-2025 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import asyncio
import argparse

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.events import Key

from flatsearch.version import get_version


class FlatSearchApp(App):
    BINDINGS = [("q", "quit", "Quit"), ("escape", "quit", "Quit")]

    def __init__(self, search_term: str, **kwargs):
        super().__init__(**kwargs)
        self.title = f"FlatSearch v{get_version()} (press ENTER to choose highlighted row)"
        self.search_term = search_term
        self.apps_data = []
        self.selected_app = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="apps_table")
        yield Footer()

    async def on_mount(self) -> None:
        """Run flatpak search and populate the table."""
        cmd = [
            "flatpak",
            "search",
            "--columns=name,description,application,version",
            *self.search_term.split(),
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            self.exit(message=f"Error executing flatpak search:\n{stderr.decode().strip()}")
            return

        output = stdout.decode()
        self.apps_data = self.parse_flatpak_output(output)
        if not self.apps_data:
            self.exit(message=f"No results found for search term '{self.search_term}'.")
            return

        table: DataTable = self.query_one("#apps_table", DataTable)
        table.cursor_type = "row"
        table.add_column("No.", width=4)
        table.add_column("Name", width=20)
        table.add_column("Description", width=50)
        table.add_column("App ID", width=30)
        table.add_column("Version", width=10)

        for row in self.apps_data:
            table.add_row(*row)

        table.focus()

    @staticmethod
    def parse_flatpak_output(output: str):
        apps = []
        for row, line in enumerate(output.strip().splitlines()):
            parts = line.split("\t")
            if len(parts) == 4:
                name, description, app_id, version = parts
                apps.append([str(row + 1), name, description, app_id, version])
        return apps

    async def on_key(self, event: Key) -> None:
        if event.key == "enter":
            table: DataTable = self.query_one("#apps_table", DataTable)
            if table.cursor_row is None:
                return
            try:
                self.selected_app = self.apps_data[table.cursor_row]
            except IndexError:
                return
            self.exit()


def parse_args(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog="flatsearch",
        description="Search Flatpak apps in a Textual TUI and optionally install the selected app.",
    )
    parser.add_argument(
        "-y", "--assumeyes", action="store_true",
        help="Assume 'yes' for installation prompts (applies to install only)."
    )
    # Everything after options is the search term; require at least one token
    parser.add_argument(
        "search", nargs="+", help="Search term and/or filters passed to 'flatpak search'."
    )
    args = parser.parse_args(argv)
    return " ".join(args.search), args.assumeyes


def main():
    if len(sys.argv) == 1:
        print("Usage: flatsearch [-y|--assumeyes] <search term>")
        sys.exit(1)

    search_term, assume_yes = parse_args(sys.argv[1:])

    app = FlatSearchApp(search_term)
    app.run()

    if app.selected_app is not None:
        _, app_name, _, app_id, _ = app.selected_app
        if assume_yes:
            # Non-interactive install
            try:
                os.execvp("flatpak", ["flatpak", "install", "-y", app_id])
            except FileNotFoundError:
                print("Error: flatpak command not found.")
                sys.exit(1)
            except Exception as e:
                print(f"Unexpected error: {e}")
                sys.exit(1)
        else:
            confirm = input(f"Install '{app_name}' ({app_id})? (y/n): ")
            if confirm.strip().lower().startswith("y"):
                try:
                    os.execvp("flatpak", ["flatpak", "install", app_id])
                except FileNotFoundError:
                    print("Error: flatpak command not found.")
                    sys.exit(1)
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    sys.exit(1)
            else:
                print("Installation cancelled.")
    else:
        print("No application was selected.")


if __name__ == "__main__":
    main()
