# pylint: disable=missing-module-docstring,invalid-name

# Note that this value will be overwritten by calls to `python ../../Build.py update_version` based
# on changes observed in the git repository. The default value below will be used until the value
# here is explicitly updated by the Continuous Integration system.
__version__ = "0.1.0"

from .Lib import GenerateStyle, GetSemanticVersion, GetSemanticVersionResult

__all__ = [
    "GenerateStyle",
    "GetSemanticVersion",
    "GetSemanticVersionResult",
]
