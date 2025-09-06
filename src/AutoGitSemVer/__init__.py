# noqa: D104
from importlib.metadata import version

from .Lib import GenerateStyle, GetSemanticVersion, GetSemanticVersionResult


__version__ = version("AutoGitSemVer")

__all__ = [
    "GenerateStyle",
    "GetSemanticVersion",
    "GetSemanticVersionResult",
]
