import argparse
import logging
import os
from pathlib import Path

import flowsql.app.parse as parse
import flowsql.app.populate as populate
import flowsql.app.draw as draw
import flowsql.app.scan as scan


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
    "--logging",
    default="debug",  # TODO : Update to "error"
    help="Set the level of logging messages to receive | Options are [debug, info, warning, error, critical] | Default value = debug",
)

args = parser.parse_args()


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


def open_drawing(output_filename: Path):
    try:
        os.system("open {}".format(output_filename))
    except:
        logging.error("Unable to open .drawio file")


def cleanup(working_dir: Path):
    """
    Cleanup working environment
    """
    filelist = [f for f in os.listdir(working_dir)]
    for f in filelist:
        os.remove(os.path.join(working_dir, f))
    os.rmdir(working_dir)


if __name__ == "__main__":
    set_logger(args.logging)

    working_dir = Path("./working-files/")
    output_filename = args.output + "/output.drawio"

    setup(working_dir=working_dir)

    paths = scan.main(args.path)

    for i in range(0, len(paths)):
        path = paths[i]
        logging.info(f"Processing file {i+1} of {len(paths)}: {path}")
        parse.main(path)

    populate.main(working_dir=working_dir)
    draw.main(output_filename=output_filename, working_dir=working_dir)

    cleanup(working_dir=working_dir)

    open_drawing(output_filename)
