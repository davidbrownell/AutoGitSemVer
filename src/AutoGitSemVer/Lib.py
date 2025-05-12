# ----------------------------------------------------------------------
# |
# |  Lib.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2024-01-21 17:14:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2024
# |  Distributed under the MIT License.
# |
# ----------------------------------------------------------------------
"""Contains functionality used to generate a semantic version based on recent changes in an active git repository."""

import itertools
import json
import os
import platform
import re

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path, PurePath
from typing import Any, Callable, cast, ClassVar, Generator, Optional

import git
import rtyaml  # type: ignore [import-untyped]

from dbrownell_Common.InflectEx import inflect  # type: ignore [import-untyped]
from dbrownell_Common import PathEx  # type: ignore [import-untyped]
from dbrownell_Common.Streams.DoneManager import DoneManager  # type: ignore [import-untyped]
from jsonschema import Draft202012Validator, validators  # type: ignore [import-untyped]
from semantic_version import Version as SemVer  # type: ignore [import-untyped]


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
DEFAULT_CONFIGURATION_FILENAMES: list[str] = [
    "AutoGitSemVer.json",
    "AutoGitSemVer.yaml",
    "AutoGitSemVer.yml",
]


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Configuration:
    """Data used to configure how the semantic version is generated."""

    # pylint: disable=too-many-instance-attributes

    # ----------------------------------------------------------------------
    filename: Optional[Path]

    version_prefix: Optional[str]

    prerelease_environment_variable_name: str

    initial_version: SemVer
    main_branch_names: list[str]

    additional_dependencies: list[Path]

    include_branch_name_when_necessary: bool = field(kw_only=True)
    include_timestamp_when_necessary: bool = field(kw_only=True)
    include_computer_name_when_necessary: bool = field(kw_only=True)


# ----------------------------------------------------------------------
class GenerateStyle(str, Enum):
    """Specifies the style by which the semantic version is generated."""

    Standard = "Standard"  # Uses both prerelease and build metadata: "1.2.3-prerelease+METADATA"
    AllPrerelease = "AllPrerelease"  # Combines metadata with prerelease data: "1.2.3-prerelease.METADATA"
    AllMetadata = "AllMetadata"  # Combines prerelease data with metadata: "1.2.3+prerelease.METADATA"


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class GetSemanticVersionResult:
    """Result of GetSemanticVersion."""

    configuration_filename: Optional[Path]
    semantic_version: SemVer
    semantic_version_string: str


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CommitInfo:
    """Information about a commit."""

    # ----------------------------------------------------------------------
    WORKING_CHANGES_COMMIT_ID: ClassVar[str] = "<working>"

    id: str
    description: str
    tags: list[str]

    author: str
    author_date: datetime

    files: list[PurePath]


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VersionDelta:
    """Information about a delta applied to a semantic version based on information found in a commit."""

    # ----------------------------------------------------------------------
    major: int
    minor: int
    patch: int

    prerelease: Optional[str]
    build_metadata: Optional[str]

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        return "{}.{}.{}{}{}".format(
            self.major,
            self.minor,
            self.patch,
            "-{}".format(self.prerelease) if self.prerelease else "",
            "+{}".format(self.build_metadata) if self.build_metadata else "",
        )


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def DefaultCommitDataExtractor(
    dm: DoneManager,  # pylint: disable=unused-argument
    commit_info: CommitInfo,
) -> Optional[VersionDelta]:
    """Default function used to extract semantic version deltas from git commits."""

    if "+major" in commit_info.description:
        return VersionDelta(1, 0, 0, None, None)
    if "+minor" in commit_info.description:
        return VersionDelta(0, 1, 0, None, None)
    if "+patch" in commit_info.description:
        return VersionDelta(0, 0, 1, None, None)
    if "+feature" in commit_info.description:
        return VersionDelta(0, 1, 0, None, None)

    return VersionDelta(0, 0, 1, None, None)


# ----------------------------------------------------------------------
def GetSemanticVersion(
    dm: DoneManager,
    path: Path,
    *,
    prerelease_name: Optional[str] = None,
    include_branch_name_when_necessary: bool = True,
    include_timestamp_when_necessary: bool = True,
    include_computer_name_when_necessary: bool = True,
    no_prefix: bool = False,
    no_metadata: bool = False,
    configuration_filenames: Optional[list[str]] = None,
    style: GenerateStyle = GenerateStyle.Standard,
    commit_delta_extraction_func: Callable[
        [
            DoneManager,
            CommitInfo,
        ],
        Optional[VersionDelta],  # None indicates that the commit does not impact the version
    ] = DefaultCommitDataExtractor,
) -> GetSemanticVersionResult:
    """Returns a semantic version based on git changes that impact the specified path."""

    configuration_filenames = configuration_filenames or DEFAULT_CONFIGURATION_FILENAMES

    repository_root = GetGitRoot(path)
    if repository_root is None:
        raise Exception("'{}' does not appear to be a git repository.".format(path))

    # Get the most applicable configuration
    configuration: Optional[Configuration] = None

    # ----------------------------------------------------------------------
    def DisplayConfiguration() -> str:
        if configuration is None:
            return "configuration errors were encountered"

        if configuration.filename is None:
            return "default configuration info will be used"

        return "configuration info found at '{}'".format(configuration.filename)

    # ----------------------------------------------------------------------

    with dm.Nested(
        "Loading AutoGitSemVer configuration...",
        DisplayConfiguration,
    ):
        configuration = GetConfiguration(path, configuration_filenames)

    changes_processed: int = 0
    version_deltas: list[VersionDelta] = []

    with dm.Nested(
        "Enumerating changes...",
        [
            lambda: "{} processed".format(inflect.no("change", changes_processed)),
            lambda: "{} applied [{:.02f}%]".format(
                inflect.no("change", len(version_deltas)),
                0 if changes_processed == 0 else ((len(version_deltas) / changes_processed) * 100),
            ),
        ],
    ) as enumerate_dm:
        root_path = configuration.filename.parent if configuration.filename else repository_root

        additional_dependency_lookup: set[Path] = set()

        for additional_dependency in configuration.additional_dependencies:
            if additional_dependency.is_file():
                additional_dependency_lookup.add(additional_dependency)
                continue

            if additional_dependency.is_dir():
                for ad_root, _, ad_filenames in os.walk(additional_dependency):
                    ad_root_path = Path(ad_root)

                    for ad_filename in ad_filenames:
                        additional_dependency_lookup.add(ad_root_path / ad_filename)

                continue

            assert False, additional_dependency  # pragma: no cover

        # ----------------------------------------------------------------------
        def IsAdditionalDependency(
            filename: Path,
        ) -> bool:
            return filename in additional_dependency_lookup

        # ----------------------------------------------------------------------
        def GetConfigurationPathForFile(
            filename: Path,
        ) -> Path:
            result = GetConfigurationFilename(filename.parent, configuration_filenames)

            if result is not None:
                return result.parent

            return repository_root

        # ----------------------------------------------------------------------
        def ShouldProcess(
            commit: CommitInfo,
        ) -> bool:
            for filename in commit.files:
                fullpath = repository_root / filename

                if (
                    PathEx.IsDescendant(fullpath, root_path)
                    and GetConfigurationPathForFile(fullpath) == root_path
                ) or IsAdditionalDependency(fullpath):
                    return True

            return False

        # ----------------------------------------------------------------------

        version_regex_str = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-(?P<prerelease>[^\+]+))?(?:\+(?P<metadata>.+))?"

        if configuration.version_prefix:
            version_regex_str = r"^{}{}{}$".format(
                re.escape(configuration.version_prefix),
                "" if configuration.version_prefix.endswith("v") else "v?",
                version_regex_str,
            )
        else:
            version_regex_str = r"^v?{}$".format(version_regex_str)

        version_regex = re.compile(version_regex_str)

        # ----------------------------------------------------------------------
        def ExtractVersionFromTags(
            tags: list[str],
        ) -> Optional[VersionDelta]:
            for tag in tags:
                match = version_regex.search(tag)
                if match is None:
                    continue

                return VersionDelta(
                    int(match.group("major")),
                    int(match.group("minor")),
                    int(match.group("patch")),
                    match.group("prerelease"),
                    match.group("metadata"),
                )

            return None

        # ----------------------------------------------------------------------

        repo = git.Repo(repository_root)

        initial_version = VersionDelta(
            configuration.initial_version.major or 0,
            configuration.initial_version.minor or 0,
            configuration.initial_version.patch or 0,
            None,
            None,
        )

        for commit in EnumCommits(repo):
            changes_processed += 1

            if not ShouldProcess(commit):
                continue

            delta_applied: Optional[VersionDelta] = None

            with enumerate_dm.VerboseNested(
                "Processing '{}' ({})".format(commit.id, commit.author_date),
                lambda: str(delta_applied) if delta_applied else None,
            ):
                delta_applied = ExtractVersionFromTags(commit.tags)
                if delta_applied is not None:
                    initial_version = delta_applied
                    break

                delta_applied = commit_delta_extraction_func(enumerate_dm, commit)
                if delta_applied is None:
                    continue

                version_deltas.append(delta_applied)

    with dm.Nested("Calculating semantic version...") as calculate_dm:
        major = initial_version.major
        minor = initial_version.minor
        patch = initial_version.patch

        prerelease: list[str] = list(initial_version.prerelease or [])
        metadata: list[str] = list(initial_version.build_metadata or [])

        for version_delta in reversed(version_deltas):
            if version_delta.major:
                major += version_delta.major
                minor = 0
                patch = 0

                prerelease = []
                metadata = []

            if version_delta.minor:
                minor += version_delta.minor
                patch = 0

                prerelease = []
                metadata = []

            if version_delta.patch:
                patch += version_delta.patch

                prerelease = []
                metadata = []

            if version_delta.prerelease:
                prerelease.append(version_delta.prerelease)
            if version_delta.build_metadata:
                metadata.append(version_delta.build_metadata)

        if major == 0 and minor == 0:
            # If here, we are going to bump the minor version, so subtract a value from the patch value
            minor = 1

            if patch > 0:
                patch -= 1

        # Augment the prerelease items (if necessary)
        augmented_prerelease: list[str] = []

        prerelease_name = prerelease_name or os.getenv(  # pylint: disable=invalid-envvar-value
            configuration.prerelease_environment_variable_name
        )
        if prerelease_name is not None:
            augmented_prerelease.append(prerelease_name)

        # ----------------------------------------------------------------------
        def GetBranchName() -> str:
            try:
                return repo.active_branch.name
            except TypeError:
                return "<detached head>"

        # ----------------------------------------------------------------------

        branch_name = GetBranchName()

        if (
            configuration.include_branch_name_when_necessary
            and include_branch_name_when_necessary
            and branch_name not in configuration.main_branch_names
        ):
            augmented_prerelease.append(branch_name)

        # Augment the metadata items (if necessary)
        augmented_metadata: list[str] = []

        if configuration.include_timestamp_when_necessary and include_timestamp_when_necessary:
            now = datetime.now()

            augmented_metadata.append(
                "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(
                    now.year,
                    now.month,
                    now.day,
                    now.hour,
                    now.minute,
                    now.second,
                ),
            )

        if configuration.include_computer_name_when_necessary and include_computer_name_when_necessary:
            augmented_metadata.append(platform.node())

        if repo.is_dirty():
            augmented_metadata.append("working_changes")

        # Combine the elements
        prerelease = augmented_prerelease + prerelease
        metadata = augmented_metadata + metadata

        if style == GenerateStyle.Standard:
            # No changes are necessary
            pass
        elif style == GenerateStyle.AllPrerelease:
            prerelease += metadata
            metadata = []
        elif style == GenerateStyle.AllMetadata:
            metadata = prerelease + metadata
            prerelease = []
        else:
            assert False, style  # pragma: no cover

        # Create the semantic version
        semver = SemVer(
            major=major,
            minor=minor,
            patch=patch,
            prerelease=(None if no_prefix else tuple(prerelease)),
            build=None if no_metadata else tuple(metadata),
        )

        semver_string = f"{configuration.version_prefix or ''}{semver}"

        calculate_dm.WriteLine(semver_string)

    return GetSemanticVersionResult(configuration.filename, semver, semver_string)


# ----------------------------------------------------------------------
def GetConfiguration(
    path: Path,
    configuration_filenames: Optional[list[str]] = None,
) -> Configuration:
    """Returns the configuration data impacting the specified path."""

    # Get the configuration filename
    configuration_filename: Optional[Path] = GetConfigurationFilename(path, configuration_filenames)

    # Get the configuration content
    configuration_content: dict[str, Any] = {}

    if configuration_filename is not None:
        with configuration_filename.open() as f:
            if configuration_filename.suffix in [".yaml", ".yml"]:
                configuration_content = cast(dict[str, Any], rtyaml.load(f))
            elif configuration_filename.suffix == ".json":
                configuration_content = json.load(f)
            else:
                assert False, configuration_filename  # pragma: no cover

    # Load the schema
    schema_filename = Path(__file__).parent / "AutoGitSemVerSchema.json"
    if not schema_filename.is_file():
        raise Exception("The filename '{}' does not exist.".format(schema_filename))  # pragma: no cover

    with schema_filename.open() as f:
        schema_content = json.load(f)

    # Create the configuration validator. The special class is augmented to apply defaults to the
    # configuration. This code is based on https://python-jsonschema.readthedocs.io/en/latest/faq/
    validator_class = Draft202012Validator
    validate_properties = validator_class.VALIDATORS["properties"]  # type: ignore

    # ----------------------------------------------------------------------
    def SetDefaults(validator, properties, instance, schema):
        for prop, sub_schema in properties.items():
            default_schema = sub_schema.get("default", None)
            if default_schema is not None:
                instance.setdefault(prop, default_schema)

            for error in validate_properties(validator, properties, instance, schema):
                yield error

    # ----------------------------------------------------------------------

    validator = validators.extend(validator_class, {"properties": SetDefaults})(schema_content)

    # Validate the configuration data
    validator.validate(configuration_content)

    additional_dependencies: list[Path] = []

    if configuration_filename is not None:
        for additional_dependency in configuration_content.get("additional_dependencies", []):
            fullpath = (configuration_filename.parent / additional_dependency).resolve()

            if not fullpath.exists():
                raise Exception("The additional dependency '{}' does not exist.".format(fullpath))

            additional_dependencies.append(fullpath)

    return Configuration(
        configuration_filename,
        configuration_content.get("version_prefix", None),
        configuration_content["prerelease_environment_variable_name"],
        SemVer.coerce(configuration_content["initial_version"]),
        configuration_content["main_branch_names"],
        additional_dependencies,
        include_branch_name_when_necessary=configuration_content["include_branch_name_when_necessary"],
        include_timestamp_when_necessary=configuration_content["include_timestamp_when_necessary"],
        include_computer_name_when_necessary=configuration_content["include_computer_name_when_necessary"],
    )


# ----------------------------------------------------------------------
def GetConfigurationFilename(
    path: Path,
    configuration_filenames: Optional[list[str]] = None,
) -> Optional[Path]:
    """Returns the configuration filename impacting the specified path."""

    configuration_filenames = configuration_filenames or DEFAULT_CONFIGURATION_FILENAMES

    for parent in itertools.chain([path], path.parents):
        for potential_configuration_filename in configuration_filenames:
            potential_filename = parent / potential_configuration_filename
            if potential_filename.is_file():
                return potential_filename

        if (parent / ".git").is_dir():
            break

    return None


# ----------------------------------------------------------------------
def GetGitRoot(path: Path) -> Optional[Path]:
    """Returns the root of the git repository associated with the provided path."""

    for root in itertools.chain([path], path.parents):
        if (root / ".git").is_dir():
            return root

    return None


# ----------------------------------------------------------------------
def EnumCommits(
    repo_or_path: git.Repo | Path,
) -> Generator[CommitInfo, None, None]:
    """Enumerates git commits for the specified repository and branch."""

    if isinstance(repo_or_path, Path):
        repo = git.Repo(repo_or_path)
    elif isinstance(repo_or_path, git.Repo):
        repo = repo_or_path
    else:
        assert False, repo_or_path  # pragma: no cover

    # Return the working changes (if any)
    if repo.is_dirty():
        yield CommitInfo(
            CommitInfo.WORKING_CHANGES_COMMIT_ID,
            "",
            [],
            "",
            datetime.now(),
            [PurePath(diff.a_path) for diff in repo.active_branch.commit.diff()],
        )

    # Enumerate commits
    git_tags: dict[str, list[git.Tag]] = {}

    for tag in repo.tags:
        # Tags are most often associated with merges into a mainline branch, but we are filtering merges
        # out in the code below. Therefore, associate the tag with a parent that isn't a merge commit.
        if len(tag.commit.parents) == 1:
            # We are looking at a direct commit to the branch
            git_tags.setdefault(tag.commit.hexsha, []).append(tag)
        else:
            # We are looking at a merge
            for parent in tag.commit.parents:
                if len(parent.parents) == 1:
                    git_tags.setdefault(parent.hexsha, []).append(tag)
                    break

    offset = 0

    while True:
        commits = list(repo.iter_commits("HEAD", max_count=50, skip=offset))
        if not commits:
            break

        offset += len(commits)

        for commit in commits:
            # Ignore merge commits
            if len(commit.parents) > 1:
                continue

            assert isinstance(commit.message, str), commit.message

            yield CommitInfo(
                commit.hexsha,
                commit.message,
                [tag.name for tag in git_tags.get(commit.hexsha, [])],
                commit.author.name or "",
                commit.authored_datetime,
                [PurePath(path) for path in commit.stats.files],
            )
