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
from typing import Optional

import typer
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.events import Key

from flatsearch.version import get_version
from flatsearch.uninstall import run_uninstall, run_list

cli = typer.Typer(
    help="FlatSearch - Search and install/uninstall Flatpak applications via TUI.",
    add_completion=False,
)


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
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        except asyncio.TimeoutError:
            process.kill()
            self.exit(message="Error: flatpak search timed out after 30 seconds.")
            return
        if process.returncode != 0:
            self.exit(message=f"Error executing flatpak search:\n{stderr.decode('utf-8').strip()}")
            return

        output = stdout.decode("utf-8")
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
        skipped = 0
        for row, line in enumerate(output.strip().splitlines()):
            parts = line.split("\t")
            if len(parts) == 4:
                name, description, app_id, version = parts
                apps.append([str(row + 1 - skipped), name, description, app_id, version])
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


@cli.command()
def uninstall(
    filter_term: Optional[list[str]] = typer.Argument(
        None, help="Optional filter to match installed app names or IDs."
    ),
    assumeyes: bool = typer.Option(False, "-y", "--assumeyes", help="Assume 'yes' for uninstallation prompts."),
) -> None:
    """Uninstall a Flatpak application via TUI."""
    filter_str = " ".join(filter_term) if filter_term else ""
    run_uninstall(filter_str, assumeyes)


@cli.command("list")
def list_apps(
    filter_term: Optional[list[str]] = typer.Argument(
        None, help="Optional filter to match installed app names or IDs."
    ),
) -> None:
    """List installed Flatpak applications and optionally launch one."""
    filter_str = " ".join(filter_term) if filter_term else ""
    run_list(filter_str)


@cli.command()
def search(
    search_terms: list[str] = typer.Argument(..., help="Search term(s) passed to 'flatpak search'."),
    assumeyes: bool = typer.Option(False, "-y", "--assumeyes", help="Assume 'yes' for installation prompts."),
) -> None:
    """Search and install Flatpak applications via TUI."""
    search_term = " ".join(search_terms)

    app = FlatSearchApp(search_term)
    app.run()

    if app.selected_app is not None:
        _, app_name, _, app_id, _ = app.selected_app
        if assumeyes:
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


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
