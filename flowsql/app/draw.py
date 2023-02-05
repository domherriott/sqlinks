import pickle
from jinja2 import Environment, FileSystemLoader
import os
import logging
from pathlib import Path


def gen_drawing(tables):
    file_loader = FileSystemLoader("flowsql/app/templates")
    env = Environment(loader=file_loader)

    template = env.get_template("drawio_template.xml")

    output = template.render(tables=tables)
    return output


def save_drawing(output, output_filename):
    with open(output_filename, "w+") as f:
        f.write(output)


def open_drawing(output_filename):
    try:
        os.system("open {}".format(output_filename))
    except:
        logging.error("Unable to open .drawio file")


def save_drawing(output, output_filename):
    with open(output_filename, "w+") as f:
        f.write(output)


def main(working_dir: Path, output_filename: Path):

    # reload object from file
    with open(working_dir / "tables.pkl", "rb") as f:
        tables = pickle.load(f)

    # logging.debug(tables)

    output = gen_drawing(tables)
    logging.debug(output_filename)

    save_drawing(output, output_filename)
    open_drawing(output_filename)
