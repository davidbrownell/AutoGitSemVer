# ----------------------------------------------------------------------
# |
# |  Lib_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2024-01-26 07:26:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2024
# |  Distributed under the MIT License.
# |
# ----------------------------------------------------------------------
"""Unit test for AutoGitSemVer/Lib.py"""

import re
import textwrap

from io import StringIO
from unittest.mock import patch
from uuid import uuid4

import pytest

from dbrownell_Common import SubprocessEx  # type: ignore [import-untyped]

from AutoGitSemVer.Lib import *  # type: ignore [import-untyped]


# ----------------------------------------------------------------------
def test_EnumCommits(tmp_path_factory):
    # Create the scenario
    repo_dir = tmp_path_factory.mktemp("repo")

    assert SubprocessEx.Run("git init", cwd=repo_dir).returncode == 0
    assert SubprocessEx.Run('git config user.name "Test User"', cwd=repo_dir).returncode == 0
    assert SubprocessEx.Run('git config user.email "a@b.com"', cwd=repo_dir).returncode == 0

    # Commit 1
    for index in range(2):
        with (repo_dir / "FileA{}.txt".format(index)).open("w") as f:
            pass

    assert SubprocessEx.Run("git add .", cwd=repo_dir).returncode == 0
    assert SubprocessEx.Run('git commit -m "Commit 1"', cwd=repo_dir).returncode == 0

    # Commit 2
    for index in range(1):
        with (repo_dir / "FileB{}.txt".format(index)).open("w") as f:
            pass

    assert SubprocessEx.Run("git add .", cwd=repo_dir).returncode == 0
    assert SubprocessEx.Run('git commit -m "Commit 2"', cwd=repo_dir).returncode == 0

    # Working
    for index in range(4):
        with (repo_dir / "FileC{}.txt".format(index)).open("w") as f:
            pass

    # ----------------------------------------------------------------------
    def Validate(
        commits: list[CommitInfo],
    ) -> None:
        # Commit #2
        assert commits[-2].id != CommitInfo.WORKING_CHANGES_COMMIT_ID
        assert commits[-2].files == [
            PurePath("FileB0.txt"),
        ]

        # Commit #1
        assert commits[-1].id != CommitInfo.WORKING_CHANGES_COMMIT_ID
        assert commits[-1].files == [
            PurePath("FileA0.txt"),
            PurePath("FileA1.txt"),
        ]

    # ----------------------------------------------------------------------

    # Scenario #1: Working changes, but nothing staged
    commits = list(EnumCommits(repo_dir))

    Validate(commits)

    assert len(commits) == 2

    # Scenario #2: Some staged changes
    assert SubprocessEx.Run("git add FileC1.txt FileC3.txt", cwd=repo_dir).returncode == 0

    commits = list(EnumCommits(repo_dir))

    Validate(commits)

    assert len(commits) == 3
    assert commits[0].id == CommitInfo.WORKING_CHANGES_COMMIT_ID
    assert commits[0].files == [
        PurePath("FileC1.txt"),
        PurePath("FileC3.txt"),
    ]


# ----------------------------------------------------------------------
def test_GetGitRoot():
    this_dir = Path(__file__).parent
    assert GetGitRoot(this_dir) == this_dir.parent
    assert GetGitRoot(this_dir.parent.parent) is None


# ----------------------------------------------------------------------
def test_GetConfigurationFilename():
    this_dir = Path(__file__).parent

    assert GetConfigurationFilename(this_dir) is None
    assert (
        GetConfigurationFilename(this_dir.parent / "src" / "AutoGitSemVer")
        == this_dir.parent / "src" / "AutoGitSemVer.yaml"
    )


# ----------------------------------------------------------------------
class TestGetConfiguration:
    # ----------------------------------------------------------------------
    def test_Default(self):
        configuration = GetConfiguration(Path(__file__).parent)

        assert configuration.filename is None
        assert configuration.include_branch_name_when_necessary
        assert configuration.include_computer_name_when_necessary
        assert configuration.include_timestamp_when_necessary
        assert configuration.initial_version == SemVer("0.0.0")
        assert configuration.main_branch_names == ["main", "master", "default"]
        assert configuration.prerelease_environment_variable_name == "AUTO_GIT_SEM_VER_PRERELEASE_NAME"
        assert configuration.version_prefix is None
        assert configuration.additional_dependencies == []

    # ----------------------------------------------------------------------
    def test_Yaml(self, tmp_path_factory):
        root = tmp_path_factory.mktemp("root")

        with (root / "one").open("w") as f:
            pass

        with (root / "two").open("w") as f:
            pass

        with (root / "AutoGitSemVer.yaml").open("w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    {
                        include_branch_name_when_necessary: false,
                        include_computer_name_when_necessary: false,
                        include_timestamp_when_necessary: false,
                        initial_version: 1.2.3,
                        main_branch_names: [ "foo", "bar" ],
                        prerelease_environment_variable_name: "BAZ",
                        additional_dependencies: ["one", "two"]
                    }
                    """,
                ),
            )

        configuration = GetConfiguration(root)

        assert configuration.filename == root / "AutoGitSemVer.yaml"
        assert not configuration.include_branch_name_when_necessary
        assert not configuration.include_computer_name_when_necessary
        assert not configuration.include_timestamp_when_necessary
        assert configuration.initial_version == SemVer("1.2.3")
        assert configuration.main_branch_names == ["foo", "bar"]
        assert configuration.prerelease_environment_variable_name == "BAZ"
        assert configuration.version_prefix is None
        assert configuration.additional_dependencies == [root / "one", root / "two"]

    # ----------------------------------------------------------------------
    def test_Yml(self, tmp_path_factory):
        root = tmp_path_factory.mktemp("root")

        with (root / "AutoGitSemVer.yml").open("w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    {
                        include_timestamp_when_necessary: false,
                        initial_version: 1.2.3,
                        version_prefix: "Test-v"
                    }
                    """,
                ),
            )

        configuration = GetConfiguration(root)

        assert configuration.filename == root / "AutoGitSemVer.yml"
        assert configuration.include_branch_name_when_necessary
        assert configuration.include_computer_name_when_necessary
        assert not configuration.include_timestamp_when_necessary
        assert configuration.initial_version == SemVer("1.2.3")
        assert configuration.main_branch_names == ["main", "master", "default"]
        assert configuration.prerelease_environment_variable_name == "AUTO_GIT_SEM_VER_PRERELEASE_NAME"
        assert configuration.version_prefix == "Test-v"
        assert configuration.additional_dependencies == []

    # ----------------------------------------------------------------------
    def test_Json(self, tmp_path_factory):
        root = tmp_path_factory.mktemp("root")

        with (root / "AutoGitSemVer.json").open("w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    {
                        "include_branch_name_when_necessary": false
                    }
                    """,
                ),
            )

        configuration = GetConfiguration(root)

        assert configuration.filename == root / "AutoGitSemVer.json"
        assert not configuration.include_branch_name_when_necessary
        assert configuration.include_computer_name_when_necessary
        assert configuration.include_timestamp_when_necessary
        assert configuration.initial_version == SemVer("0.0.0")
        assert configuration.main_branch_names == ["main", "master", "default"]
        assert configuration.prerelease_environment_variable_name == "AUTO_GIT_SEM_VER_PRERELEASE_NAME"
        assert configuration.version_prefix is None
        assert configuration.additional_dependencies == []

    # ----------------------------------------------------------------------
    def test_Invalid(self, tmp_path_factory):
        root = tmp_path_factory.mktemp("root")

        with (root / "AutoGitSemVer.yaml").open("w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    {
                        include_branch_name_when_necessary: "This is not a valid value"
                    }
                    """,
                ),
            )

        with pytest.raises(
            Exception,
            match=re.compile("'This is not a valid value' is not of type 'boolean'.*", re.DOTALL),
        ):
            GetConfiguration(root)


# ----------------------------------------------------------------------
class TestSemanticVersion:
    # ----------------------------------------------------------------------
    def test_Empty(self):
        result, semver = _GetSemanticVersionImpl([])

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 0

    # ----------------------------------------------------------------------
    def test_Single(self):
        result, semver = _GetSemanticVersionImpl([_CreateCommitInfo("Commit 1")])

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 0

    # ----------------------------------------------------------------------
    def test_Multiple(self):
        commits = [
            _CreateCommitInfo("Commit 3"),
            _CreateCommitInfo("Commit 2"),
            _CreateCommitInfo("Commit 1"),
        ]

        result, semver = _GetSemanticVersionImpl(commits)

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == len(commits) - 1

    # ----------------------------------------------------------------------
    def test_BumpMinor(self):
        result, semver = _GetSemanticVersionImpl(
            [
                _CreateCommitInfo("Bump Patch 3"),
                _CreateCommitInfo("Bump Minor (+minor)"),  # This will reset the patch
                _CreateCommitInfo("Bump Patch 2"),
                _CreateCommitInfo("Bump Patch 1"),
            ],
        )

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 1

    # ----------------------------------------------------------------------
    def test_BumpMajor(self):
        result, semver = _GetSemanticVersionImpl(
            [
                _CreateCommitInfo("Bump Patch (+patch)"),
                _CreateCommitInfo("Bump Minor (+minor)"),
                _CreateCommitInfo("Bump Major (+major)"),  # This will reset the minor
                _CreateCommitInfo("Bump Minor (+minor)"),
                _CreateCommitInfo("Bump Minor (+minor)"),
                _CreateCommitInfo("Bump Minor (+minor)"),
            ],
        )

        assert result == 0
        assert semver.semantic_version.major == 1
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 1

    # ----------------------------------------------------------------------
    def test_Feature(self):
        result, semver = _GetSemanticVersionImpl(
            [
                _CreateCommitInfo("Feature 1 (+features)"),
                _CreateCommitInfo("Feature 2 (+feature)"),
                _CreateCommitInfo("Feature 3 (+features)"),
            ],
        )

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 3
        assert semver.semantic_version.patch == 0

    # ----------------------------------------------------------------------
    def test_WithTag(self):
        result, semver = _GetSemanticVersionImpl(
            [
                _CreateCommitInfo("(+major)"),
                _CreateCommitInfo("(+minor)"),
                _CreateCommitInfo("(+patch)"),
                _CreateCommitInfo("Tag", tags=["Ignore Me", "1.2.3"]),
            ],
        )

        assert result == 0
        assert semver.semantic_version.major == 2
        assert semver.semantic_version.minor == 0
        assert semver.semantic_version.patch == 0

    # ----------------------------------------------------------------------
    def test_WithTag2(self):
        result, semver = _GetSemanticVersionImpl(
            [
                _CreateCommitInfo(""),
                _CreateCommitInfo("", tags=["1.2.3"]),
            ],
        )

        assert result == 0
        assert semver.semantic_version.major == 1
        assert semver.semantic_version.minor == 2
        assert semver.semantic_version.patch == 4

    # ----------------------------------------------------------------------
    def test_PrereleaseName(self):
        result, semver = _GetSemanticVersionImpl([], prerelease_name="MyPrereleaseName")

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 0
        assert (
            semver.semantic_version.prerelease and semver.semantic_version.prerelease[0] == "MyPrereleaseName"
        )

    # ----------------------------------------------------------------------
    def test_IgnoredChanges(self):
        result, semver = _GetSemanticVersionImpl(
            [
                _CreateCommitInfo("Ignored 1", files=[PurePath("Ignored.txt")]),
                _CreateCommitInfo("Included 1", files=[PurePath("src/Included.txt")]),
                _CreateCommitInfo("Ignored 2", files=[PurePath("Ignored.txt")]),
                _CreateCommitInfo("Included 2", files=[PurePath("src/Included.txt")]),
                _CreateCommitInfo("Ignored 3", files=[PurePath("Ignored.txt")]),
                _CreateCommitInfo("Included 3", files=[PurePath("src/Included.txt")]),
            ],
            working_dir=Path(__file__).parent.parent / "src",
        )

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 2

    # ----------------------------------------------------------------------
    def test_Styles(self):
        # Standard
        result, semver = _GetSemanticVersionImpl(
            [],
            prerelease_name="MyPrereleaseName",
            style=GenerateStyle.Standard,
        )

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 0

        assert semver.semantic_version.prerelease is not None and len(semver.semantic_version.prerelease) >= 1
        standard_prerelease = semver.semantic_version.prerelease

        assert semver.semantic_version.build is not None and len(semver.semantic_version.build) >= 1
        standard_build = semver.semantic_version.build

        # AllPrerelease
        result, semver = _GetSemanticVersionImpl(
            [],
            prerelease_name="MyPrereleaseName",
            style=GenerateStyle.AllPrerelease,
        )

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 0

        assert semver.semantic_version.prerelease is not None and (
            len(semver.semantic_version.prerelease) == len(standard_prerelease) + len(standard_build)
        )
        assert semver.semantic_version.build == ()

        # AllMetadata
        result, semver = _GetSemanticVersionImpl(
            [],
            prerelease_name="MyPrereleaseName",
            style=GenerateStyle.AllMetadata,
        )

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 0

        assert semver.semantic_version.prerelease == ()
        assert semver.semantic_version.build is not None and (
            len(semver.semantic_version.build) == len(standard_prerelease) + len(standard_build)
        )

    # ----------------------------------------------------------------------
    def test_CustomDeltaFunc(self):
        # ----------------------------------------------------------------------
        def CustomCommitDeltaExtractor(
            dm: DoneManager,
            commit_info: CommitInfo,
        ) -> Optional[VersionDelta]:
            if "MAJOR" in commit_info.description:
                return VersionDelta(1000, 0, 0, "bumped_major", None)
            if "MINOR" in commit_info.description:
                return VersionDelta(0, 100, 0, "bumped_minor", None)
            if "PATCH" in commit_info.description:
                return VersionDelta(0, 0, 10, None, "bumped_patch")

            return None

        result, semver = _GetSemanticVersionImpl(
            [
                _CreateCommitInfo("PATCH"),
                _CreateCommitInfo(""),
                _CreateCommitInfo("MINOR"),
                _CreateCommitInfo(""),
                _CreateCommitInfo("MAJOR"),
                _CreateCommitInfo(""),
            ],
            commit_delta_extraction_func=CustomCommitDeltaExtractor,
        )

        assert result == 0
        assert semver.semantic_version.major == 1000
        assert semver.semantic_version.minor == 100
        assert semver.semantic_version.patch == 10
        assert (
            semver.semantic_version.prerelease is None
            or "bumped_major" not in semver.semantic_version.prerelease
        )  # prerelease is wiped when a new version is encountered
        assert (
            semver.semantic_version.prerelease is None
            or "bumped_minor" not in semver.semantic_version.prerelease
        )  # prerelease is wiped when a new version is encountered
        assert semver.semantic_version.build and "bumped_patch" in semver.semantic_version.build

    # ----------------------------------------------------------------------
    def test_String(self):
        result, semver = _GetSemanticVersionImpl([])

        assert result == 0
        assert semver.semantic_version.major == 0
        assert semver.semantic_version.minor == 1
        assert semver.semantic_version.patch == 0
        assert semver.semantic_version_string != "0.1.0"

        result, semver = _GetSemanticVersionImpl(
            [],
            include_branch_name_when_necessary=False,
            include_timestamp_when_necessary=False,
            include_computer_name_when_necessary=False,
            no_metadata=True,
        )
        assert semver.semantic_version_string == "0.1.0"


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CreateCommitInfo(
    description: str,
    files: Optional[list[PurePath]] = None,
    tags: Optional[list[str]] = None,
    *,
    is_working_change: bool = False,
) -> CommitInfo:
    id = CommitInfo.WORKING_CHANGES_COMMIT_ID if is_working_change else str(uuid4())

    if files is None:
        files = [PurePath("File.txt")]

    return CommitInfo(id, description, tags or [], "Author", datetime.now(), files)


# ----------------------------------------------------------------------
def _GetSemanticVersionImpl(
    commits: list[CommitInfo],
    *,
    working_dir: Path = Path.cwd(),
    **kwargs,
) -> tuple[int, GetSemanticVersionResult]:
    with patch("AutoGitSemVer.Lib.EnumCommits", return_value=commits):
        sink = StringIO()

        with DoneManager.Create(sink, "_GetSemanticVersionImpl...") as dm:
            result = GetSemanticVersion(dm, working_dir, **kwargs)

        return dm.result, result
