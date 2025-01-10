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

from typer.testing import CliRunner
from AutoGitSemVer import GetSemanticVersionResult
from AutoGitSemVer.scripts.UpdatePythonVersion import app


# ----------------------------------------------------------------------
def test_Default():
    _Execute(
        textwrap.dedent(
            """\
            # Line Before
                __version__ = ""
            # Line After
            """,
        ),
        textwrap.dedent(
            """\
            # Line Before
                __version__ = "1.2.3"
            # Line After
            """,
        ),
    )


# ----------------------------------------------------------------------
def test_NoVersion():
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
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    original: str,
    expected: str,
    *,
    expected_failure: bool = False,
) -> str:
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
        result = CliRunner().invoke(app, [__file__])

        if expected_failure:
            assert result.exit_code != 0
        else:
            assert result.exit_code == 0

        return result.output
