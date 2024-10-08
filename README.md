# AutoGitSemVer

<!-- BEGIN: Exclude Package -->
<!-- [BEGIN] Badges -->
[![License](https://img.shields.io/github/license/davidbrownell/AutoGitSemVer?color=dark-green)](https://github.com/davidbrownell/AutoGitSemVer/blob/master/LICENSE.txt)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/davidbrownell/AutoGitSemVer?color=dark-green)](https://github.com/davidbrownell/AutoGitSemVer/commits/main/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/AutoGitSemVer?color=dark-green)](https://pypi.org/project/AutoGitSemVer/)
[![PyPI - Version](https://img.shields.io/pypi/v/AutoGitSemVer?color=dark-green)](https://pypi.org/project/AutoGitSemVer/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/autogitsemver)](https://pypistats.org/packages/autogitsemver)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9043/badge)](https://www.bestpractices.dev/projects/9043)
[![Code Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/davidbrownell/f15146b1b8fdc0a5d45ac0eb786a84f7/raw/AutoGitSemVer_coverage.json)](https://github.com/davidbrownell/AutoGitSemVer/actions)
<!-- [END] Badges -->
<!-- END: Exclude Package -->

Generate a semantic version based on commits made to a git repository.

<!-- BEGIN: Exclude Package -->
## Contents
- [Overview](#overview)
- [Installation](#installation)
- [Development](#development)
- [Additional Information](#additional-information)
- [License](#license)
<!-- END: Exclude Package -->

## Overview
AutoGitSemVer uses commits in a git repository to calculate a semantic version. A commit's title and/or description can be used to increment a specific part of the semantic version and configuration files can be applied to control how the semantic version is generated. Finally, multiple, distinct semantic versions can be generated from different directories within the source tree.

### How to use AutoGitSemVer
#### Running the Executable

From a terminal window, run:

<table>
    <tr>
        <th>Scenario</th>
        <th>Command Line</th>
        <th>Output</th>
    </tr>
    <tr>
        <td>Standard</td>
        <td><code>autogitsemver</code></td>
        <td>
<pre style="background-color: black; color: #AAAAAA; font-size: .75em">Loading AutoGitSemVer configuration...DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.001464, default configuration info will be used)
Enumerating changes...DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.193258, 1 change processed, no changes applied [0.00%])
Calculating semantic version...
  0.6.1+20240318122529.BROWNELL08
DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.054236)
&nbsp;
Results: DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.267488)</pre>
       </td>
    </tr>
    <tr>
      <td>Without Metadata</td>
      <td><code>autogitsemver --no-metadata</code></td>
      <td>
<pre style="background-color: black; color: #AAAAAA; font-size: .75em">Loading AutoGitSemVer configuration...DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.001468, default configuration info will be used)
Enumerating changes...DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.201744, 1 change processed, no changes applied [0.00%])
Calculating semantic version...
  0.6.1
DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.060190)
&nbsp;
Results: DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.281524)</pre>
      </td>
    </tr>
    <tr>
        <td>Quiet</td>
        <td><code>autogitsemver --quiet</code></td>
        <td>
<pre style="background-color: black; color: #AAAAAA; font-size: .75em">0.6.1+20240318122751.BROWNELL08</pre>
        </td>
    </tr>
    <tr>
        <td>Verbose</td>
        <td><code>autogitsemver --verbose</code></td>
        <td>
<pre style="background-color: black; color: #AAAAAA; font-size: .75em">Loading AutoGitSemVer configuration...DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.001416, default configuration info will be used)
Enumerating changes...
  VERBOSE: Processing '11c41919cb2ed8ef26542665fc9caa6544081457' (2024-03-09 11:53:11-05:00)...DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.000049, 0.6.1)
DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.192439, 1 change processed, no changes applied [0.00%])
Calculating semantic version...
  0.6.1+20240318122836.BROWNELL08
DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.053696)
&nbsp;
Results: DONE! (<span style="font-weight: bold; color: #00aa00">0</span>, 0:00:00.265691)</pre>
        </td>
    </tr>
    <tr>
        <td>Display Help</td>
        <td><code>autogitsemver --help</code></td>
        <td>
<pre style="background-color: black; color: #AAAAAA; font-size: .75em">&nbsp;
 Usage: autogitsemver [OPTIONS] [PATH]
&nbsp;
 Automatically generates semantic versions based on changes in a git repository.
&nbsp;
┌─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│   path      [PATH]  Generate a semantic version based on changes that impact the specified path. [default: C:\Code\AutoGitSemVer]                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ --style                     [Standard|AllPrerelease|AllMetadata]  Specifies the way in which the semantic version is generated; this is useful when targets using the generated │
│                                                                   semantic version do not fully support the semantic version specification.                                     │
│                                                                   [default: GenerateStyle.Standard]                                                                             │
│ --prerelease-name           TEXT                                  Create a semantic version string with this prerelease name. [default: None]                                   │
│ --no-prefix                                                       Do not include the prefix in the generated semantic version.                                                  │
│ --no-branch-name                                                  Do not include the branch name in the prerelease section of the generated semantic version.                   │
│ --no-metadata                                                     Do not include the build metadata section of the generated semantic version.                                  │
│ --verbose                                                         Write verbose information to the terminal.                                                                    │
│ --debug                                                           Write debug information to the terminal.                                                                      │
│ --quiet                                                           Do not display any information other than the generated semantic version.                                     │
│ --version                                                         Display the version of this tool and exit.                                                                    │
│ --install-completion        [bash|zsh|fish|powershell|pwsh]       Install completion for the specified shell. [default: None]                                                   │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]       Show completion for the specified shell, to copy it or customize the installation. [default: None]            │
│ --help                                                            Show this message and exit.                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘</pre>
        </td>
    </tr>
    <tr>
        <td>Version</td>
        <td><code>autogitsemver --version</code></td>
        <td>
<pre style="background-color: black; color: #AAAAAA; font-size: .75em">autogitsemver v0.7.0</pre>
        </td>
    </tr>
</table>

#### Running with Python

```python
from io import StringIO
from pathlib import Path

from AutoGitSemVer import GetSemanticVersion
from dbrownell_Common.Streams.DoneManager import DoneManager


with DoneManager.Create(StringIO(), "") as dm:
    path = Path.cwd()

    result = GetSemanticVersion(dm, path)

print(result.semantic_version_string)
```

#### Updating the Version

A simplified [semantic version](https://semver.org) is defined by a `major` number, a `minor` number, and a `patch` number in the form:

    <major>.<minor>.<patch>

Changes to each of these numbers convey different meanings to those who have taken a dependency on the solution decorated by a semantic version:

- Changes to a `major` number indicate that backwards-**incompatible** functionality was introduced.
- Changes to a `minor` number indicate that backwards-**compatible** functionality was introduced.
- Changes to a `patch` number indicate that changes were introduced (but those changes did not introduce new functionality).

By default, AutoGitSemVer will increment the `patch` number for each git commit encountered.

##### Customizing the Update
The following tokens can be added anywhere in a git commit's title or description to increment the `major`, `minor`, or `patch` numbers:

| Semantic Version Number | Git Comment Token(s) | Example |
| --- | --- | --- |
| `major` | `+major` | 1.2.3 -> 2.0.0 |
| `minor` | `+minor`, `+feature` | 1.2.3 -> 1.3.0 |
| `patch` | `+patch` | 1.2.3 -> 1.2.4 |

##### Examples

###### Modifier in the Description

| | |
|-|-|
| Git Commit Title: | `Added feature Foo` |
| Git Commit Description: | `Foo lets a user... +minor` |

###### Modifier in the Title

| | |
|-|-|
| Git Commit Title: | `Added feature Foo (+minor)` |
| Git Commit Description: | `Foo lets a user...` |

#### Advanced Configuration

##### Configuration Files

The way in which semantic versions are generated can be customized through configuration files named:

- `AutoGitSemVer.json`
- `AutoGitSemVer.yaml`
- `AutoGitSemVer.yml`

These configuration files will impact the semantic versions generated for any changes in files or directories in the directory or its children. For example, given the directory structure:

```
<root>
|- File1.txt
|- DirectoryA
   |- AutoGitSemVer.json
   |- FileA.txt
   |- DirectoryA.1
      |- FileA1.txt
|- DirectoryB
   |- AutoGitSemVer.yaml
   |- FileB.txt
```

| File with Changes | Configuration Filename |
| --- | --- |
| `File1.txt` | None |
| `FileA.txt` | `DirectoryA/AutoGitSemVer.json` |
| `FileA1.txt` | `DirectoryA/AutoGitSemVer.json` |
| `FileB.txt` | `DirectoryB/AutoGitSemVer.yaml` |

The configuration file used when generating the semantic version is displayed when running AutoGitSemVer.

Information about the contents of these configuration files can be found in [AutoGitSemVerSchema.SimpleSchema](https://github.com/davidbrownell/AutoGitSemVer/blob/main/src/ConfigurationSchema/AutoGitSemVerSchema.SimpleSchema).

A simple example of a configuration file can be found [here](https://github.com/davidbrownell/AutoGitSemVer/blob/main/src/AutoGitSemVer.yaml).

<!-- BEGIN: Exclude Package -->
## Installation
<!-- [BEGIN] Installation -->
AutoGitSemVer can be installed via one of these methods:

- [Installation via Executable](#installation-via-executable)
- [Installation via pip](#installation-via-pip)

### Installation via Executable
Download an executable for Linux, MacOS, or Windows to the the functionality provided by this repository without a dependency on python.

1. Download the archive for the latest release [here](https://github.com/davidbrownell/AutoGitSemVer/releases/latest). The filename will begin with `exe.` and contain the name of your operating system.
2. Decompress the archive.

#### Verifying Signed Executables
Executables are signed and validated using [Minisign](https://jedisct1.github.io/minisign/). The public key used to verify the signature of the executable is `RWSGe+8DKCW2QmYfuJMyqBR2MtboMxx+F/cLB1C8DGKd9ZSchpVQBytP`.

To verify that the executable is valid, download the corresponding `.minisig` file [here](https://github.com/davidbrownell/AutoGitSemVer/releases/latest) and run this command, replacing `<filename>` with the name of the file to be verified:

`docker run -i --rm -v .:/host jedisct1/minisign -V -P RWSGe+8DKCW2QmYfuJMyqBR2MtboMxx+F/cLB1C8DGKd9ZSchpVQBytP -m /host/<filename>`

Instructions for installing [docker](https://docker.com) are available at https://docs.docker.com/engine/install/.

### Installation via pip
To install the AutoGitSemVer package via [pip](https://pip.pypa.io/en/stable/) (Python Installer for Python) for use with your python code:

`pip install AutoGitSemVer`

<!-- [END] Installation -->

## Development
<!-- [BEGIN] Development -->
Please visit [Contributing](https://github.com/davidbrownell/AutoGitSemVer/blob/main/CONTRIBUTING.md) and [Development](https://github.com/davidbrownell/AutoGitSemVer/blob/main/DEVELOPMENT.md) for information on contributing to this project.<!-- [END] Development -->

<!-- END: Exclude Package -->

## Additional Information
Additional information can be found at these locations.

<!-- [BEGIN] Additional Information -->
| Title | Document | Description |
| --- | --- | --- |
| Code of Conduct | [CODE_OF_CONDUCT.md](https://github.com/davidbrownell/AutoGitSemVer/blob/main/CODE_OF_CONDUCT.md) | Information about the the norms, rules, and responsibilities we adhere to when participating in this open source community. |
| Contributing | [CONTRIBUTING.md](https://github.com/davidbrownell/AutoGitSemVer/blob/main/CONTRIBUTING.md) | Information about contributing code changes to this project. |
| Development | [DEVELOPMENT.md](https://github.com/davidbrownell/AutoGitSemVer/blob/main/DEVELOPMENT.md) | Information about development activities involved in making changes to this project. |
| Governance | [GOVERNANCE.md](https://github.com/davidbrownell/AutoGitSemVer/blob/main/GOVERNANCE.md) | Information about how this project is governed. |
| Maintainers | [MAINTAINERS.md](https://github.com/davidbrownell/AutoGitSemVer/blob/main/MAINTAINERS.md) | Information about individuals who maintain this project. |
| Security | [SECURITY.md](https://github.com/davidbrownell/AutoGitSemVer/blob/main/SECURITY.md) | Information about how to privately report security issues associated with this project. |
<!-- [END] Additional Information -->

## License

AutoGitSemVer is licensed under the <a href="https://choosealicense.com/licenses/mit/" target="_blank">MIT</a> license.
