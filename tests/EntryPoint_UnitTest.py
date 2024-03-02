# ----------------------------------------------------------------------
# |
# |  EntryPoint_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2024-03-02 11:38:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2024
# |  Distributed under the MIT License.
# |
# ----------------------------------------------------------------------
# """Unit tests for EntryPoint.py."""

from pathlib import Path
from typing import Any, Mapping
from unittest.mock import MagicMock as Mock, patch

from typer.testing import CliRunner

from AutoGitSemVer import GenerateStyle, GetSemanticVersionResult
from AutoGitSemVer.EntryPoint import app


# ----------------------------------------------------------------------
def test_Default():
    output, args, kwargs = _Execute()

    assert len(args) == 2
    assert args[1] == Path.cwd()

    assert len(kwargs) == 5
    assert kwargs["prerelease_name"] is None
    assert kwargs["include_branch_name_when_necessary"] is True
    assert kwargs["no_prefix"] is False
    assert kwargs["no_metadata"] is False
    assert kwargs["style"] == GenerateStyle.Standard


# ----------------------------------------------------------------------
def test_CustomPath():
    custom_path = Path(__file__).parent.parent

    output, args, kwargs = _Execute(str(custom_path))

    assert len(args) == 2
    assert args[1] == custom_path


# ----------------------------------------------------------------------
def test_NonBoolArgs():
    output, args, kwargs = _Execute(
        "--prerelease-name",
        "prerelease_name",
        "--style",
        "AllPrerelease",
    )

    assert len(args) == 2
    assert args[1] == Path.cwd()

    assert len(kwargs) == 5
    assert kwargs["prerelease_name"] == "prerelease_name"
    assert kwargs["include_branch_name_when_necessary"] is True
    assert kwargs["no_prefix"] is False
    assert kwargs["no_metadata"] is False
    assert kwargs["style"] == GenerateStyle.AllPrerelease


# ----------------------------------------------------------------------
def test_BoolIncludeBranchNameWhenNecessary():
    output, args, kwargs = _Execute(
        "--no-branch-name",
    )

    assert len(kwargs) == 5
    assert kwargs["prerelease_name"] is None
    assert kwargs["include_branch_name_when_necessary"] is False
    assert kwargs["no_prefix"] is False
    assert kwargs["no_metadata"] is False
    assert kwargs["style"] == GenerateStyle.Standard


# ----------------------------------------------------------------------
def test_BoolNoPrefix():
    output, args, kwargs = _Execute(
        "--no-prefix",
    )

    assert len(kwargs) == 5
    assert kwargs["prerelease_name"] is None
    assert kwargs["include_branch_name_when_necessary"] is True
    assert kwargs["no_prefix"] is True
    assert kwargs["no_metadata"] is False
    assert kwargs["style"] == GenerateStyle.Standard


# ----------------------------------------------------------------------
def test_BoolNoMetadata():
    output, args, kwargs = _Execute(
        "--no-metadata",
    )

    assert len(kwargs) == 5
    assert kwargs["prerelease_name"] is None
    assert kwargs["include_branch_name_when_necessary"] is True
    assert kwargs["no_prefix"] is False
    assert kwargs["no_metadata"] is True
    assert kwargs["style"] == GenerateStyle.Standard


# ----------------------------------------------------------------------
def test_Quiet():
    output, args, kwargs = _Execute()
    assert output != "1.2.3"

    output, args, kwargs = _Execute("--quiet")
    assert output == "1.2.3"


# ----------------------------------------------------------------------
def test_Version():
    output, args, kwargs = _Execute("--version")
    assert output.startswith("autogitsemver v")

    assert not args
    assert not kwargs


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    *args,
) -> tuple[str, tuple[Any, ...], Mapping[str, Any]]:
    with patch(
        "AutoGitSemVer.EntryPoint.GetSemanticVersion",
        return_value=GetSemanticVersionResult(None, Mock(), "1.2.3"),
    ) as mock:
        result = CliRunner().invoke(app, list(args))
        assert result.exit_code == 0

        if not mock.call_args_list:
            return result.output, (), {}

        assert len(mock.call_args_list) == 1
        return result.output, mock.call_args_list[0].args, mock.call_args_list[0].kwargs
