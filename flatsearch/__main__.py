"""
MIT License

Copyright (c) 2018-2023 Marp team (marp-team@marp.app)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import subprocess
import sys

from rich import print
from rich.table import Table
from rich.prompt import InvalidResponse, IntPrompt, Confirm


def is_number(value: str, min_v=0, max_v=sys.maxsize) -> str:
    """validator"""
    if value.isdigit():
        return value
    raise InvalidResponse(
        f"[orange]Please enter a valid integer between {min_v} and {max_v}.[/orange]"
    )


def parse_flatpak_output(output):
    apps = []
    for row, line in enumerate(output.strip().splitlines()):
        parts = line.split("\t")  # Split into a maximum of 6 parts
        if len(parts) == 4:
            name, description, app_id, version = parts
            apps.append([str(row), name, description, app_id, version])
    return apps


def main():
    arguments = sys.argv
    if len(arguments) < 2:
        print(f"[red]ERROR[/red]: Correct call must contain search information. E.g.:")
        print(f"       [white]>[/white] [yellow]flatsearch[/yellow] [cyan]comic[/cyan]")
        return

    term = " ".join(arguments[1:])
    term = f'"{term}"'

    print(f"command: [yellow]flatsearch[/yellow] [cyan]{term}[/cyan]")

    result = subprocess.run(
        ["flatpak", "search", "--columns=name,description,application,version"]
        + arguments[1:],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        print(f"[red]ERROR[/red]:")
        print(result.stderr)
        return

    text = result.stdout
    apps_data = parse_flatpak_output(text)

    table = Table(title="Flatpak Search Results")

    table.add_column("", style="white", no_wrap=True)
    table.add_column("Name", style="cyan", no_wrap=True, min_width=25)
    table.add_column("Description", style="magenta", no_wrap=False)
    table.add_column("App ID", style="yellow", no_wrap=True)
    table.add_column("Version", style="green", no_wrap=True)

    for app in apps_data:
        table.add_row(*app)

    print(table)

    choice_count = len(apps_data)
    user_input = IntPrompt.ask(
        f"Please enter a number (1-{choice_count} or ENTER to quit)",
        choices=[str(i) for i in range(1, choice_count)],
        show_choices=False,
        default=""
    )

    try:
        if not user_input.strip():
            print('[yellow]No Choice Indicated.[/yellow]')
            print('Done.')
            return
    except AttributeError:
        # they entered a number, so it doesn't have a .strip attribute
        ...

    row_num, app_name, app_desc, app_id, app_version = apps_data[user_input]

    response = Confirm.ask(f"Ask flatpak to install '{app_name}' ({app_id})?")

    if response:
        # starting in new session because we are about to quit
        subprocess.Popen(["flatpak", "install", str(app_id)], start_new_session=True)
    else:
        print('[yellow]No Install Indicated.[/yellow]')
        print('Done.')

    sys.exit()


if __name__ == "__main__":

    main()
