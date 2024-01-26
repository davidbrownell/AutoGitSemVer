# ----------------------------------------------------------------------
# |
# |  EntryPoint.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2024-01-24 20:13:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2024
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automatically generates semantic versions based on changes in a git repository."""

from pathlib import Path
from typing import Annotated, Optional

import typer

from dbrownell_Common.ContextlibEx import ExitStack  # type: ignore [import-untyped]
from dbrownell_Common.Streams.DoneManager import DoneManager, Flags as DoneManagerFlags  # type: ignore [import-untyped]
from dbrownell_Common.Streams.StreamDecorator import TextWriterT  # type: ignore [import-untyped]
from typer.core import TyperGroup  # type: ignore [import-untyped]

from AutoGitSemVer import GenerateStyle, GetSemanticVersion, GetSemanticVersionResult


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):
    # pylint: disable=missing-class-docstring
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.commands.keys()


# ----------------------------------------------------------------------
app = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
@app.command(
    "Generate",
    help=__doc__,
    no_args_is_help=False,
)
def Generate(
    path: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
            exists=True,
            resolve_path=True,
            help="Generate a semantic version based on changes that impact the specified path.",
        ),
    ] = Path.cwd(),
    style: Annotated[
        GenerateStyle,
        typer.Option(
            "--style",
            case_sensitive=False,
            help="Specifies the way in which the semantic version is generated; this is useful when targets using the generated semantic version do not fully support the semantic version specification.",
        ),
    ] = GenerateStyle.Standard,
    prerelease_name: Annotated[
        Optional[str],
        typer.Option(
            "--prerelease-name",
            help="Create a semantic version string with this prerelease name.",
        ),
    ] = None,
    no_prefix: Annotated[
        bool,
        typer.Option(
            "--no-prefix",
            help="Do not include the prefix in the generated semantic version.",
        ),
    ] = False,
    no_branch_name: Annotated[
        bool,
        typer.Option(
            "--no-branch-name",
            help="Do not include the branch name in the prerelease section of the generated semantic version.",
        ),
    ] = False,
    no_metadata: Annotated[
        bool,
        typer.Option(
            "--no-metadata",
            help="Do not include the build metadata section of the generated semantic version.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="Write verbose information to the terminal.",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Write debug information to the terminal.",
        ),
    ] = False,
) -> None:
    with DoneManager.CreateCommandLine(
        flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ) as dm:
        GetSemanticVersion(
            dm,
            path,
            prerelease_name=prerelease_name,
            include_branch_name_when_necessary=not no_branch_name,
            no_prefix=no_prefix,
            no_metadata=no_metadata,
            style=style,
        )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
