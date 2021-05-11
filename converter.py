#!/usr/bin/env python3

''' 
python executable that takes command line arguments for in_dir, out_dir
'''


import argparse
import pathlib
from collections import deque
import time
import datetime as dt
from pytz import timezone
from win32_setctime import setctime
from os import utime
from typing import Set

EASTERN = timezone('US/Eastern')
DOW = {"Monday", "Tuesday", "Wednesday",
       "Thursday", "Friday", "Saturday", "Sunday"}
INVALID_CHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']


def isTimeFormat(i):
    try:
        time.strptime(i, '%H:%M')
        return True
    except ValueError:
        return False


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Produce directories of markdown files from a copy-and-pasted directory of onenote notebooks"
    )
    parser.add_argument("input_dir", action="store",
                        help="The absolute unix-style path where the copy-and-pasted onenote notebooks are stored as text. For example 'C:/Users/Me/Documents' or '/usr/me'")
    return parser


def parse_path(input_dir: str) -> pathlib.Path:
    path = pathlib.Path(input_dir)

    if not path.exists():
        raise ValueError("Input path is not a valid path")
    elif not path.is_dir():
        raise ValueError("Input path is not a directory")

    return path


def get_notebook_lines(notebook_file: pathlib.PosixPath) -> Set[str]:
    note_lines = set()
    prev_lines = deque([], maxlen=4)

    with notebook_file.open("r", errors="ignore") as file:
        for line_num, curr_line in enumerate(file, 1):
            prev_lines.appendleft(curr_line)
            if line_num < 6:
                if line_num == 1:
                    note_lines.add(line_num)
                continue

            if (":" in curr_line and isTimeFormat(curr_line.split()[0]) and
                    prev_lines[1].split(",")[0] in DOW):
                note_lines.add(line_num - 3)
    return note_lines


def produce_markdown_files(notebook_file: pathlib.PosixPath, notebook_lines: Set[str]):
    curr_file_loc = None
    curr_title = None
    curr_datetime = None
    lines = []

    with notebook_file.open("r", encoding="utf-8") as file:
        for line_num, curr_line in enumerate(file, 1):
            # title found
            if line_num in notebook_lines:
                if curr_file_loc is not None:
                    print("writing to", curr_file_loc)
                    file = curr_file_loc.open(
                        "w", errors="strict", encoding='utf-8')
                    file.writelines(lines)
                    file.close()
                    setctime(curr_file_loc, curr_datetime)
                    utime(curr_file_loc, (curr_datetime, curr_datetime))
                    lines.clear()
                    curr_file_loc = None

                curr_title = curr_line
            # Date found
            elif line_num - 2 in notebook_lines:
                curr_datetime = dt.datetime.strptime(
                    curr_line.rstrip(), '%A, %B %d, %Y')
            # Time found
            elif line_num - 3 in notebook_lines:
                curr_datetime = dt.datetime.combine(curr_datetime,
                                                    dt.datetime.strptime(curr_line.split()[0], '%H:%M').time())
                curr_datetime = EASTERN.localize(curr_datetime)
                curr_datetime = time.mktime(curr_datetime.timetuple())
            else:
                if curr_file_loc is None and not curr_line.isspace():
                    if curr_title.isspace():
                        curr_title = ' '.join(curr_line.split()[:7])
                    else:
                        curr_title = curr_title[0:-1]

                    for char in INVALID_CHARS:
                        curr_title = curr_title.replace(char, " ")

                    curr_file_loc = notebook_file.parent / \
                        notebook_file.name[:-4] / (curr_title + ".md")
                    if not curr_file_loc.parent.exists():
                        raise ValueError()

                    print("found", curr_file_loc)
                if curr_file_loc is not None:
                    lines.append(curr_line)

    file = curr_file_loc.open("w", errors="strict", encoding='utf-8')
    file.writelines(lines)
    file.close()
    setctime(curr_file_loc, curr_datetime)
    utime(curr_file_loc, (curr_datetime, curr_datetime))
    lines.clear()


def process_text_files(in_dir: pathlib.Path) -> None:
    print(in_dir)
    for notebook_text_file in in_dir.iterdir():
        notebook_lines = get_notebook_lines(notebook_text_file)
        print(notebook_lines)
        produce_markdown_files(notebook_text_file, notebook_lines)


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    in_path = parse_path(args.input_dir)
    process_text_files(in_path)


if __name__ == "__main__":
    main()
