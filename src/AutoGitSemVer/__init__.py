# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2024-01-22 15:52:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2024
# |  Distributed under the MIT License.
# |
# ----------------------------------------------------------------------
# pylint: disable=missing-module-docstring,invalid-name

# ----------------------------------------------------------------------
# Note that this value will be overwritten by calls to `python ../../Build.py update_version` based
# on changes observed in the git repository. The default value below will be used until the value
# here is explicitly updated as part of a commit.
__version__ = "0.1.0"


from .Lib import GenerateStyle, GetSemanticVersion, GetSemanticVersionResult
