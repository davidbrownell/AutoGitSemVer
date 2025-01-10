# ----------------------------------------------------------------------
# |
# |  UpdatePythonVersion.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2025-01-10 10:04:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2025
# |  Distributed under the MIT License.
# |
# ----------------------------------------------------------------------
"""Updates a __version__ variable with the calculated version in a Python file."""

import re

from pathlib import Path
from typing import Annotated, Optional

import typer

from AutoGitSemVer import GetSemanticVersion
from dbrownell_Common.Streams.DoneManager import DoneManager, Flags as DoneManagerFlags
from typer.core import TyperGroup


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):
    # pylint: disable=missing-class-docstring
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.commands.keys()  # pragma: no cover


# ----------------------------------------------------------------------
app = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
@app.command("EntryPoint", help=__doc__, no_args_is_help=True)
def EntryPoint(
    python_filename: Annotated[
        Path,
        typer.Argument(
            dir_okay=False,
            exists=True,
            resolve_path=True,
            help="Name of the python file that contains the __version__ variable.",
        ),
    ],
    working_dir: Annotated[
        Optional[Path],
        typer.Argument(
            file_okay=False,
            exists=True,
            resolve_path=True,
            help="Working directory used to calculate the version.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Write verbose information to the terminal."),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Write debug information to the terminal."),
    ] = False,
) -> None:
    with DoneManager.CreateCommandLine(
        flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ) as dm:
        working_dir = working_dir or python_filename.parent

        version = GetSemanticVersion(
            dm,
            working_dir,
            no_metadata=True,
            include_branch_name_when_necessary=False,
            include_timestamp_when_necessary=False,
            include_computer_name_when_necessary=False,
        )

        dm.WriteLine("")

        with dm.Nested(f"Updating '{python_filename}'...") as update_dm:
            with python_filename.open(encoding="utf-8") as f:
                content = f.read()

            match = re.search(
                r"^(?P<prefix>\s*__version__\s*=\s*)(?P<quote>['\"])\S*?(?P=quote)(?P<newline>\r?\n)",
                content,
                flags=re.MULTILINE,
            )
            if not match:
                update_dm.WriteError("A '__version__' variable was not found.\n")
                return

            content = "".join(
                [
                    content[: match.start()],
                    match.group("prefix"),
                    match.group("quote"),
                    version.semantic_version_string,
                    match.group("quote"),
                    match.group("newline"),
                    content[match.end() :],
                ],
            )

            with python_filename.open("w", encoding="utf-8", newline=match.group("newline")) as f:
                f.write(content)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
