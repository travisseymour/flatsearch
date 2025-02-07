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

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.events import Key

from flatsearch.version import get_version


class FlatSearchApp(App):
    """
    This tool uses the Textual framework to display a scrollable table of search results from flatpak.
    Use the arrow keys to select an entry and press ENTER to choose an app.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, search_term: str, **kwargs):
        super().__init__(**kwargs)
        self.title = f"FlatSearch v{get_version()} (press ENTER to choose highlighted row)"
        self.search_term = search_term
        self.apps_data = []  # Will hold list of search results
        self.selected_app = None  # Will hold the selected app's row

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="apps_table")
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app starts. Run the flatpak search and build the table."""
        # Execute the flatpak search command
        args = self.search_term.split()
        process = await asyncio.create_subprocess_exec(
            "flatpak",
            "search",
            "--columns=name,description,application,version",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            error_text = stderr.decode().strip()
            self.exit(message=f"Error executing flatpak search:\n{error_text}")
            return

        output = stdout.decode()
        self.apps_data = self.parse_flatpak_output(output)
        if not self.apps_data:
            self.exit(message=f"No results found for search term '{self.search_term}'.")
            return

        description_width = 50  # Maximum width for the Description column

        # Get the DataTable widget and set it up.
        table: DataTable = self.query_one("#apps_table", DataTable)
        table.cursor_type = "row"  # Allow row-by-row navigation.
        table.add_column("No.", width=4)
        table.add_column("Name", width=20)
        table.add_column("Description", width=description_width)
        table.add_column("App ID", width=30)
        table.add_column("Version", width=10)

        for row in self.apps_data:
            table.add_row(*row)

        # Focus the table so the user can navigate with arrow keys.
        table.focus()

    @staticmethod
    def parse_flatpak_output(output: str):
        """
        Parse the flatpak output (expected as tab-delimited lines with 4 fields) and
        return a list of rows formatted for display.
        """
        apps = []
        for row, line in enumerate(output.strip().splitlines()):
            parts = line.split("\t")
            if len(parts) == 4:
                name, description, app_id, version = parts
                # Prepend a serial number for display.
                apps.append([str(row + 1), name, description, app_id, version])
        return apps

    async def on_key(self, event: Key) -> None:
        """
        Listen for the ENTER key. When pressed, store the currently highlighted row
        and then exit the TUI.
        """
        if event.key == "enter":
            table: DataTable = self.query_one("#apps_table", DataTable)
            if table.cursor_row is None:
                return  # Nothing is selected

            row_index = table.cursor_row
            try:
                # Each row is: [number, name, description, app_id, version]
                self.selected_app = self.apps_data[row_index]
            except IndexError:
                return

            # Exit the TUI; control returns to main() after app.run()
            self.exit()


def main():
    if len(sys.argv) < 2:
        print("Usage: flatsearch <search term>")
        sys.exit(1)
    search_term = " ".join(sys.argv[1:])
    app = FlatSearchApp(search_term)
    app.run()  # Run the TUI; this call will return once self.exit() is called

    # After exiting the TUI, check if the user selected an app.
    if app.selected_app is not None:
        # Each row is: [number, name, description, app_id, version]
        _, app_name, _, app_id, _ = app.selected_app
        # Use standard prompting to confirm installation.
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
