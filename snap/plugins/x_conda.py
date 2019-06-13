# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This plugin just dumps the content from a specified source.

This plugin uses the common plugin keywords as well as those for 'sources'.
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

In the cases where dumping the content needs some mangling or organizing
one would take advantage of the core functionalities available to plugins
such as: `filesets`, `stage`, `snap` and `organize`.
"""

import re
import os

import snapcraft
from snapcraft.internal import errors
from snapcraft import file_utils

class DumpInvalidSymlinkError(errors.SnapcraftError):
    fmt = (
        "Failed to copy {path!r}: it's a symlink pointing outside the snap.\n"
        "Fix it to be valid when snapped and try again."
    )

    def __init__(self, path):
        super().__init__(path=path)


class XCondaDump(snapcraft.BasePlugin):
    @classmethod
    def schema(cls):
        schema = super().schema()
        schema["required"] = ["source"]
        return schema

    def enable_cross_compilation(self):
        pass

    def build(self):
        super().build()
        snapcraft.file_utils.link_or_copy_tree(
            self.builddir,
            self.installdir,
            copy_function=lambda src, dst: _link_or_copy(src, dst, self.installdir),
        )
        rewrite_python_shebangs(self.installdir)


def rewrite_python_shebangs(root_dir):
    """Recursively change #!/usr/bin/pythonX shebangs to #!/usr/bin/env pythonX

    :param str root_dir: Directory that will be crawled for shebangs.
    """

    file_pattern = re.compile(r"")
    argless_shebang_pattern = re.compile(r"\A#!.*(python\S*)$", re.MULTILINE)
    shebang_pattern_with_args = re.compile(
        r"\A#!.*(python\S*)[ \t\f\v]+(\S+)$", re.MULTILINE
    )

    file_utils.replace_in_file(
        root_dir, file_pattern, argless_shebang_pattern, r"#!/usr/bin/env \1"
    )

    # The above rewrite will barf if the shebang includes any args to python.
    # For example, if the shebang was `#!/usr/bin/python3 -Es`, just replacing
    # that with `#!/usr/bin/env python3 -Es` isn't going to work as `env`
    # doesn't support arguments like that.
    #
    # The solution is to replace the shebang with one pointing to /bin/sh, and
    # then exec the original shebang with included arguments. This requires
    # some quoting hacks to ensure the file can be interpreted by both sh as
    # well as python, but it's better than shipping our own `env`.
    file_utils.replace_in_file(
        root_dir,
        file_pattern,
        shebang_pattern_with_args,
        r"""#!/bin/sh\n''''exec \1 \2 -- "$0" "$@" # '''""",
    )


def _link_or_copy(source, destination, boundary):
    """Attempt to copy symlinks as symlinks unless pointing out of boundary."""

    follow_symlinks = False

    # If this is a symlink, analyze where it's pointing and make sure it will
    # still be valid when snapped. If it won't, follow the symlink when
    # copying (i.e. copy the file to which the symlink is pointing instead).
    if os.path.islink(source):
        link = os.readlink(source)
        destination_dirname = os.path.dirname(destination)
        normalized = os.path.normpath(os.path.join(destination_dirname, link))
        if os.path.isabs(link) or not normalized.startswith(boundary):
            # Only follow symlinks that are NOT pointing at libc (LP: #1658774)
            if link not in snapcraft.repo.Repo.get_package_libraries("libc6"):
                follow_symlinks = True

    try:
        snapcraft.file_utils.link_or_copy(
            source, destination, follow_symlinks=follow_symlinks
        )
    except errors.SnapcraftCopyFileNotFoundError:
        raise DumpInvalidSymlinkError(source)
