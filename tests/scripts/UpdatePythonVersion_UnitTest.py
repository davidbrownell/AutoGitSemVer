# ----------------------------------------------------------------------
# |
# |  UpdatePythonVersion_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2025-01-10 12:08:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2025
# |  Distributed under the MIT License.
# |
# ----------------------------------------------------------------------
"""Unit tests for UpdatePythonVersion.py."""

import textwrap

from pathlib import Path
from unittest.mock import MagicMock as Mock, mock_open, patch

import pytest

from click.testing import Result
from typer.testing import CliRunner
from AutoGitSemVer import GetSemanticVersionResult
from AutoGitSemVer.scripts.UpdatePythonVersion import app


# ----------------------------------------------------------------------
@pytest.mark.parametrize("quote", ['"', "'", '"""', "'''"])
@pytest.mark.parametrize("prefix", ["", "    "])
@pytest.mark.parametrize("suffix", ["", "  # Comment!"])
def test_Python(quote, prefix, suffix):
    _Execute(
        textwrap.dedent(
            f"""\
            # Line Before
            {prefix}__version__ = {quote}0.0.0{quote}{suffix}
            # Line After
            """,
        ),
        textwrap.dedent(
            f"""\
            # Line Before
            {prefix}__version__ = {quote}1.2.3{quote}{suffix}
            # Line After
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_NoPythonVersion():
    _Execute(
        textwrap.dedent(
            """\
            # No __version__ in this file
            """,
        ),
        "",
        expected_failure=True,
    )


# ----------------------------------------------------------------------
@pytest.mark.parametrize("quote", ['"', '"""'])
@pytest.mark.parametrize("prefix", ["", "    "])
@pytest.mark.parametrize("suffix", ["", "  # Comment!"])
def test_Toml(quote, prefix, suffix):
    _Execute(
        textwrap.dedent(
            f"""\
            # Line Before
            {prefix}version = {quote}0.0.0{quote}{suffix}
            # Line After
            """,
        ),
        textwrap.dedent(
            f"""\
            # Line Before
            {prefix}version = {quote}1.2.3{quote}{suffix}
            # Line After
            """,
        ),
        file_extension=".toml",
    )


# ----------------------------------------------------------------------
def test_NoTomlVersion():
    _Execute(
        textwrap.dedent(
            """\
            # No version in this file
            """,
        ),
        "",
        file_extension=".toml",
        expected_failure=True,
    )


# ----------------------------------------------------------------------
def test_UnsupportedFileType():
    result = _Execute(
        "",
        "",
        file_extension=".md",
        expected_failure=True,
    )
    exception_message = str(result.exception)
    assert "README.md' is not a recognized file type." in exception_message


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    original: str,
    expected: str,
    *,
    file_extension: str = ".py",
    expected_failure: bool = False,
) -> Result:
    # ----------------------------------------------------------------------
    def MyWrite(value):
        assert value == expected

    # ----------------------------------------------------------------------

    file_mock = mock_open(read_data=original)

    handle = file_mock()
    handle.read = Mock(return_value=original)
    handle.write = MyWrite

    with (
        patch(
            "AutoGitSemVer.scripts.UpdatePythonVersion.GetSemanticVersion",
            return_value=GetSemanticVersionResult(None, Mock(), "1.2.3"),
        ),
        patch.object(Path, "open", file_mock),
    ):
        if file_extension == ".py":
            placeholder_filename = Path(__file__)
        elif file_extension == ".toml":
            placeholder_filename = Path(__file__).parent.parent.parent / "pyproject.toml"
        elif file_extension == ".md":
            placeholder_filename = Path(__file__).parent.parent.parent / "README.md"
        else:
            assert False, file_extension

        result = CliRunner().invoke(app, [str(placeholder_filename)])

        if expected_failure:
            assert result.exit_code != 0, result.output
        else:
            assert result.exit_code == 0, result.output

        return result
