import argparse
import logging
import os
from pathlib import Path

from sqlinks.app.Objects import Collection

from sqlinks.app import parse as parse
from sqlinks.app import draw as draw
from sqlinks.app import scan as scan
from sqlinks.app import open as open


def get_args():
    """_summary_

    Returns:
        _type_: _description_
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p", "--path", default=".", help="Path to scan across | Default value = ."
    )

    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Path to output diagrams | Set to 'REL' to save adjacent to scripts | Default value = .",
    )

    parser.add_argument(
        "-l",
        "--logging_level",
        default="error",
        help="Set the level of logging messages to receive | Options are [debug, info, warning, error, critical] | Default value = debug",
    )

    parser.add_argument(
        "-au",
        "--auto_open",
        default="n",
        help="Set whether the output file should be auto-opened or not after execution | Options are [y, n] | Default value = n",
    )

    args = parser.parse_args()
    return args


def set_logger(logging_level: str):
    """
    Set the logging level based off passed arguments
    """

    if logging_level == "debug":
        level = logging.DEBUG
    elif logging_level == "info":
        level = logging.INFO
    elif logging_level == "warning":
        level = logging.WARNING
    elif logging_level == "error":
        level = logging.ERROR
    elif logging_level == "critical":
        level = logging.CRITICAL
    else:
        level = logging.DEBUG

    logging.basicConfig(level=level)


def setup(working_dir: Path):
    """
    Set up working environment
    """
    os.makedirs(working_dir, exist_ok=True)


def cleanup(working_dir: Path):
    """
    Cleanup working environment
    """
    filelist = [f for f in os.listdir(working_dir)]
    for f in filelist:
        os.remove(os.path.join(working_dir, f))
    os.rmdir(working_dir)


def print_args(args):
    """Print args

    Args:
        args ():
    """
    print("\n")
    print("------------------")
    print("Selected settings")
    print("------------------")

    for key, value in vars(args).items():
        print(f"{key}: {value}")

    print("\n")
    return None


if __name__ == "__main__":
    args = get_args()
    print_args(args)
    set_logger(args.logging_level)

    working_dir = Path("./working-files/")
    output_filename = Path(args.output + "/output.md")

    setup(working_dir=working_dir)

    paths = scan.main(args.path)

    # Instantiate empty ObjectCollection
    collection = Collection()

    for i in range(0, len(paths)):
        path = paths[i]
        print("\n")
        print(f"-" * 10)
        print(f"[{i+1}]/[{len(paths)}]")
        print(f"-" * 10)
        print(f"File: {path['relative_path']}")
        collection = parse.main(collection=collection, path=path["absolute_path"])

    print("\nGenerating diagram...")

    draw.main(output_filename=output_filename, collection=collection)

    cleanup(working_dir=working_dir)

    # Open the output file if auto_open is selected
    if args.auto_open == "y":
        open.open_drawing(output_filename)
