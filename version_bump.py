from datetime import datetime
from pathlib import Path
from typing import Union


def bump_version(path_string: Union[str, Path]):
    # Get current datetime and format the version string
    now = datetime.now()
    date_string = now.strftime("%Y.%m.%d.") + str(now.hour * 60 + now.minute)

    # Write the version string to, e.g., 'flatsearch/version.py'
    Path(Path(path_string), 'version.py').write_text(f'__version__="{date_string}"\n')

    return date_string

if __name__ == '__main__':
    print('New Version:')
    print (bump_version('flatsearch'))