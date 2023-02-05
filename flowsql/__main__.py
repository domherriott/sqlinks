import argparse
import logging
import os

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


def open_drawing(output_filename):
    try:
        os.system("open {}".format(output_filename))
    except:
        logging.error("Unable to open .drawio file")


if __name__ == "__main__":
    set_logger(args.logging)
    output_filename = args.output + "/output.drawio"

    paths = scan.main(args.path)

    for i in range(0, len(paths)):
        path = paths[i]
        logging.info(f"Processing file {i+1} of {len(paths)}: {path}")

        parse.main(path)
        populate.main()
        draw.main(output_filename)

    folder = "working-files"
    filelist = [f for f in os.listdir(folder)]
    for f in filelist:
        os.remove(os.path.join(folder, f))

    open_drawing(output_filename)
