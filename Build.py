# ----------------------------------------------------------------------
# |
# |  Build.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2024-01-21 17:03:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2024
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Build tasks for this python module."""

import sys

from pathlib import Path

import typer

from dbrownell_Common import SubprocessEx  # type: ignore [import-untyped]
from dbrownell_Common.Streams.DoneManager import DoneManager  # type: ignore [import-untyped]
from dbrownell_DevTools.RepoBuildTools import Python as RepoBuildTools  # type: ignore [import-untyped]
from typer.core import TyperGroup


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):
    # pylint: disable=missing-class-docstring
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.commands.keys()


# ----------------------------------------------------------------------
this_dir = Path(__file__).parent
assert this_dir.is_dir(), this_dir

src_dir = this_dir / "src" / "AutoGitSemVer"
assert src_dir.is_dir(), src_dir

tests_dir = this_dir / "tests"
assert tests_dir.is_dir(), tests_dir


# ----------------------------------------------------------------------
app = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
Black = RepoBuildTools.BlackFuncFactory(this_dir, app)
Pylint = RepoBuildTools.PylintFuncFactory(src_dir, app)
Pytest = RepoBuildTools.PytestFuncFactory(tests_dir, "AutoGitSemVer", app, 80.0)
Package = RepoBuildTools.PackageFuncFactory(this_dir, app)
Publish = RepoBuildTools.PublishFuncFactory(this_dir, app)


# ----------------------------------------------------------------------
@app.command("UpdateVersion", no_args_is_help=False)
def UpdateVersion():
    """Updates the version"""

    with DoneManager.CreateCommandLine() as dm:
        result = SubprocessEx.Run(
            'autogitsemver "{}" --no-branch-name --no-metadata --quiet'.format(src_dir.parent)
        )

        dm.result = result.returncode

        version = result.output.strip()

        init_filename = src_dir / "__init__.py"

        with init_filename.open() as f:
            content = f.read()

        import re

        content = re.sub(
            r'__version__ = "\d+\.\d+\.\d+"',
            '__version__ = "{}"'.format(version),
            content,
            1,
        )

        with init_filename.open("w") as f:
            f.write(content)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(app())
