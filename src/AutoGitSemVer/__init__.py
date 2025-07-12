# noqa: D104

# Wheel names will be generated according to this value. Do not manually modify this value; instead
# update it according to committed changes by running this command from the root of the repository:
#
#   uv run python -m AutoGitSemVer.scripts.UpdatePythonVersion ./src/AutoGitSemVer/__init__.py ./src
#
__version__ = "0.1.0"


from .Lib import GenerateStyle, GetSemanticVersion, GetSemanticVersionResult

__all__ = [
    "GenerateStyle",
    "GetSemanticVersion",
    "GetSemanticVersionResult",
]
