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
# |  Distributed under the MIT License.
# |
# ----------------------------------------------------------------------
"""Automatically generates semantic versions based on changes in a git repository."""

import sys

from io import StringIO
from pathlib import Path
from typing import Annotated, Callable, Optional

import typer

from dbrownell_Common.ContextlibEx import ExitStack  # type: ignore [import-untyped]
from dbrownell_Common.Streams.DoneManager import DoneManager, Flags as DoneManagerFlags  # type: ignore [import-untyped]
from dbrownell_Common.Streams.StreamDecorator import TextWriterT  # type: ignore [import-untyped]
from typer.core import TyperGroup  # type: ignore [import-untyped]

from AutoGitSemVer import (
    GenerateStyle,
    GetSemanticVersion,
    GetSemanticVersionResult,
    __version__,
)


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
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Do not display any information other than the generated semantic version.",
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Display the version of this tool and exit.",
        ),
    ] = False,
) -> None:
    if version:
        sys.stdout.write("autogitsemver v{}\n".format(__version__))
        sys.exit(0)

    output_stream: Optional[TextWriterT] = None
    postprocess_func: Optional[Callable[[DoneManager, Optional[GetSemanticVersionResult]], None]] = None

    if quiet:
        sink = StringIO()

        output_stream = sink

        # ----------------------------------------------------------------------
        def PostprocessQuietData(
            dm: DoneManager,
            result: Optional[GetSemanticVersionResult],
        ) -> None:
            if dm.result != 0:
                sys.stdout.write(sink.getvalue())
            else:
                assert result is not None
                sys.stdout.write(result.semantic_version_string)

        # ----------------------------------------------------------------------

        postprocess_func = PostprocessQuietData

    else:
        output_stream = sys.stdout

        # ----------------------------------------------------------------------
        def PostprocessNone(*args, **kwargs):
            return None

        # ----------------------------------------------------------------------

        postprocess_func = PostprocessNone

    assert output_stream is not None
    assert postprocess_func is not None

    with DoneManager.CreateCommandLine(
        output_stream,
        flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ) as dm:
        result: Optional[GetSemanticVersionResult] = None

        with ExitStack(lambda: postprocess_func(dm, result)):
            result = GetSemanticVersion(
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
