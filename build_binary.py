# ----------------------------------------------------------------------
# |
# |  build_binary.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2024-02-01 11:32:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2024
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Builds an executable"""

import datetime
import importlib
import textwrap

from pathlib import Path

from cx_Freeze import setup, Executable
from dbrownell_Common import PathEx


# ----------------------------------------------------------------------
_name = "AutoGitSemVer"
_initial_year = 2024
_entry_point_script = PathEx.EnsureFile(Path(__file__).parent / "src" / _name / "EntryPoint.py")
_copyright_template = textwrap.dedent(
    """\
    Copyright David Brownell {year}{year_suffix}
    Distributed under the Boost Software License, Version 1.0. See
    copy at http://www.boost.org/LICENSE_1_0.txt.
    """,
)


# ----------------------------------------------------------------------
# Get the version and docstring
mod = importlib.import_module(_name)
_version = mod.__version__

# Get the docstring
mod = importlib.import_module("{}.{}".format(_name, _entry_point_script.stem))
_docstring = mod.__doc__

del mod


# ----------------------------------------------------------------------
# Create the year suffix
_year = datetime.datetime.now().year

if _year == _initial_year:
    _year_suffix = ""
elif _year // 100 != _initial_year // 100:
    _year_suffix = str(_year)
else:
    _year_suffix = "-{}".format(_year % 100)


# ----------------------------------------------------------------------
setup(
    name=_name,
    version=_version,
    description=_docstring,
    executables=[
        Executable(
            _entry_point_script,
            base="console",
            copyright=_copyright_template.format(
                year=str(_initial_year),
                year_suffix=_year_suffix,
            ),
            # icon=<icon_filename>,
            target_name=_name,
            # trademarks="",
        ),
    ],
    options={
        "build_exe": {
            "excludes": [
                "tcl",
                "tkinter",
            ],
            "no_compress": False,
            "optimize": 0,
            # "packages": [],
            # "include_files": [],
        },
    },
)
