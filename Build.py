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

from dbrownell_Common import PathEx  # type: ignore [import-untyped]
from dbrownell_DevTools.RepoBuildTools import Python as RepoBuildTools  # type: ignore [import-untyped]
from typer.core import TyperGroup


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):
    # pylint: disable=missing-class-docstring
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.commands.keys()


# ----------------------------------------------------------------------
this_dir = PathEx.EnsureDir(Path(__file__).parent)
src_dir = PathEx.EnsureDir(this_dir / "src" / "AutoGitSemVer")
tests_dir = PathEx.EnsureDir(this_dir / "tests")


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
UpdateVersion = RepoBuildTools.UpdateVersionFuncFactory(
    src_dir.parent,
    src_dir / "__init__.py",
    app,
)
Package = RepoBuildTools.PackageFuncFactory(this_dir, app)
Publish = RepoBuildTools.PublishFuncFactory(this_dir, app)
BuildBinary = RepoBuildTools.BuildBinaryFuncFactory(
    this_dir,
    PathEx.EnsureFile(this_dir / "src" / "BuildBinary.py"),
    app,
)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(app())
