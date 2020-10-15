#! /usr/bin/env python

# Copyright 2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentParser
from docutils.core import publish_file
import copy
import fileinput
import glob
import os
import os.path
import re
import shutil
import subprocess
import sys
import yaml

"""
Read a RST file and replace titles with a different title level if required.
Args:
    filename: The name of the file being read (for debugging)
    file_stream: The open file stream to read from.
    title_level: The integer which determines the offset to *start* from.
    title_styles: An array of characters detailing the right title styles to use
                  e.g. ["=", "-", "~", "+"]
Returns:
    string: The file contents with titles adjusted.
Example:
    Assume title_styles = ["=", "-", "~", "+"], title_level = 1, and the file
    when read line-by-line encounters the titles "===", "---", "---", "===", "---".
    This function will bump every title encountered down a sub-heading e.g.
    "=" to "-" and "-" to "~" because title_level = 1, so the output would be
    "---", "~~~", "~~~", "---", "~~~". There is no bumping "up" a title level.
"""
def load_with_adjusted_titles(filename, file_stream, title_level, title_styles):
    rst_lines = []

    prev_line_title_level = 0 # We expect the file to start with '=' titles
    file_offset = None
    prev_non_title_line = None
    for i, line in enumerate(file_stream):
        if (prev_non_title_line is None
            or not is_title_line(prev_non_title_line, line, title_styles)
        ):
            rst_lines.append(line)
            prev_non_title_line = line
            continue

        line_title_style = line[0]
        line_title_level = title_styles.index(line_title_style)

        # Not all files will start with "===" and we should be flexible enough
        # to allow that. The first title we encounter sets the "file offset"
        # which is added to the title_level desired.
        if file_offset is None:
            file_offset = line_title_level
            if file_offset != 0:
                print(("     WARNING: %s starts with a title style of '%s' but '%s' " +
                    "is preferable.") % (filename, line_title_style, title_styles[0]))

        # Sanity checks: Make sure that this file is obeying the title levels
        # specified and bail if it isn't.
        # The file is allowed to go 1 deeper or any number shallower
        if prev_line_title_level - line_title_level < -1:
            raise Exception(
                ("File '%s' line '%s' has a title " +
                "style '%s' which doesn't match one of the " +
                "allowed title styles of %s because the " +
                "title level before this line was '%s'") %
                (filename, (i + 1), line_title_style, title_styles,
                title_styles[prev_line_title_level])
            )
        prev_line_title_level = line_title_level

        adjusted_level = (
            title_level + line_title_level - file_offset
        )

        # Sanity check: Make sure we can bump down the title and we aren't at the
        # lowest level already
        if adjusted_level >= len(title_styles):
            raise Exception(
                ("Files '%s' line '%s' has a sub-title level too low and it " +
                "cannot be adjusted to fit. You can add another level to the " +
                "'title_styles' key in targets.yaml to fix this.") %
                (filename, (i + 1))
            )

        if adjusted_level == line_title_level:
            # no changes required
            rst_lines.append(line)
            continue
        # Adjusting line levels
        print(
            "File: %s Adjusting %s to %s because file_offset=%s title_offset=%s" %
            (filename, line_title_style, title_styles[adjusted_level],
                file_offset, title_level)
        )
        rst_lines.append(line.replace(
            line_title_style,
            title_styles[adjusted_level]
        ))

    return "".join(rst_lines)


def is_title_line(prev_line, line, title_styles):
    # The title underline must match at a minimum the length of the title
    if len(prev_line) > len(line):
        return False

    line = line.rstrip()

    # must be at least 3 chars long
    if len(line) < 3:
        return False

    # must start with a title char
    title_char = line[0]
    if title_char not in title_styles:
        return False

    # all characters must be the same
    for char in line[1:]:
        if char != title_char:
            return False

    # looks like a title line
    return True

in_dir = sys.argv[1]
styles = ["=", "-", "~", "+", "^", "`", "@", ":"]
out_dir = sys.argv[2]

if __name__ == '__main__':
    print(in_dir)

listing = os.listdir(in_dir)
for in_file in listing:
    print(in_file)
    rst = open(os.path.join(in_dir, in_file), 'r')
    processed = load_with_adjusted_titles(in_file, rst, 2, styles)
    open(os.path.join(out_dir, in_file), 'w').write(processed)
