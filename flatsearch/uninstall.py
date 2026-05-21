#!/usr/bin/env python3
"""
FlatSearch Uninstall Module. Provides a Textual TUI for uninstalling Flatpak applications.

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


class FlatUninstallApp(App):
    """Textual app for displaying and selecting installed Flatpak apps for uninstallation."""

    BINDINGS = [("q", "quit", "Quit"), ("escape", "quit", "Quit")]

    def __init__(self, filter_term: str = "", read_only: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.read_only = read_only
        if read_only:
            self.title = f"FlatSearch List v{get_version()} (press ENTER to launch)"
        else:
            self.title = f"FlatSearch Uninstall v{get_version()} (press ENTER to choose highlighted row)"
        self.filter_term = filter_term.lower()
        self.apps_data = []
        self.selected_app = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="apps_table")
        yield Footer()

    async def on_mount(self) -> None:
        """Run flatpak list and populate the table with installed apps."""
        cmd = [
            "flatpak",
            "list",
            "--app",
            "--columns=name,application,version,size",
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        except asyncio.TimeoutError:
            process.kill()
            self.exit(message="Error: flatpak list timed out after 30 seconds.")
            return
        if process.returncode != 0:
            self.exit(message=f"Error executing flatpak list:\n{stderr.decode('utf-8').strip()}")
            return

        output = stdout.decode("utf-8")
        self.apps_data = self.parse_flatpak_output(output)

        if self.filter_term:
            self.apps_data = [
                row
                for row in self.apps_data
                if self.filter_term in row[1].lower() or self.filter_term in row[2].lower()
            ]

        if not self.apps_data:
            if self.filter_term:
                self.exit(message=f"No installed apps found matching '{self.filter_term}'.")
            else:
                self.exit(message="No Flatpak applications are currently installed.")
            return

        # Sort alphabetically by name (case-insensitive)
        self.apps_data.sort(key=lambda row: row[1].lower())

        # Re-number rows after filtering/sorting
        for idx, row in enumerate(self.apps_data):
            row[0] = str(idx + 1)

        table: DataTable = self.query_one("#apps_table", DataTable)
        table.cursor_type = "row"
        table.add_column("No.", width=4)
        table.add_column("Name", width=25)
        table.add_column("App ID", width=40)
        table.add_column("Version", width=15)
        table.add_column("Size", width=10)

        for row in self.apps_data:
            table.add_row(*row)

        table.focus()

    @staticmethod
    def parse_flatpak_output(output: str):
        """Parse the tab-separated output from flatpak list."""
        apps = []
        skipped = 0
        for row, line in enumerate(output.strip().splitlines()):
            parts = line.split("\t")
            if len(parts) == 4:
                name, app_id, version, size = parts
                apps.append([str(row + 1 - skipped), name, app_id, version, size])
            else:
                skipped += 1
        if skipped > 0:
            print(f"Warning: Skipped {skipped} malformed line(s) from flatpak output.", file=sys.stderr)
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


def run_uninstall(filter_term: str = "", assume_yes: bool = False):
    """Run the uninstall TUI and handle the uninstallation process."""
    app = FlatUninstallApp(filter_term)
    app.run()

    if app.selected_app is not None:
        _, app_name, app_id, _, _ = app.selected_app
        if assume_yes:
            # Non-interactive uninstall
            try:
                os.execvp("flatpak", ["flatpak", "uninstall", "-y", app_id])
            except FileNotFoundError:
                print("Error: flatpak command not found.")
                sys.exit(1)
            except Exception as e:
                print(f"Unexpected error: {e}")
                sys.exit(1)
        else:
            confirm = input(f"Uninstall '{app_name}' ({app_id})? (y/n): ")
            if confirm.strip().lower().startswith("y"):
                try:
                    os.execvp("flatpak", ["flatpak", "uninstall", app_id])
                except FileNotFoundError:
                    print("Error: flatpak command not found.")
                    sys.exit(1)
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    sys.exit(1)
            else:
                print("Uninstallation cancelled.")
    else:
        print("No application was selected.")


def run_list(filter_term: str = ""):
    """Run a TUI listing installed Flatpak applications, with option to launch."""
    app = FlatUninstallApp(filter_term, read_only=True)
    app.run()

    if app.selected_app is not None:
        _, app_name, app_id, _, _ = app.selected_app
        try:
            os.execvp("flatpak", ["flatpak", "run", app_id])
        except FileNotFoundError:
            print("Error: flatpak command not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
