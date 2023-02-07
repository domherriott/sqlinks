"""draw.py."""
import pickle
from jinja2 import Environment, FileSystemLoader
import os
import logging
from pathlib import Path


def gen_drawing(tables):
    """_summary_
    Args:
        tables (_type_): _description_

    Returns:
        _type_: _description_
    """
    file_loader = FileSystemLoader("flowsql/app/templates")
    env = Environment(loader=file_loader)

    template = env.get_template("drawio_template.xml")

    output = template.render(tables=tables)
    return output


def save_drawing(output, output_filename):
    """_summary_
    Args:
        output (_type_): _description_
        output_filename (_type_): _description_
    """
    with open(output_filename, "w+") as f:
        f.write(output)


def open_drawing(output_filename):
    """_summary_
    Args:
        output_filename (_type_): _description_
    """
    try:
        os.system("open {}".format(output_filename))
    except:
        logging.error("Unable to open .drawio file")


def save_drawing(output, output_filename):
    """_summary_

    Args:
        output (_type_): _description_
        output_filename (_type_): _description_
    """
    with open(output_filename, "w+") as f:
        f.write(output)


def main(working_dir: Path, output_filename: Path):
    """_summary_

    Args:
        working_dir (Path): _description_
        output_filename (Path): _description_
    """

    # reload object from file
    with open(working_dir / "tables.pkl", "rb") as f:
        tables = pickle.load(f)

    # logging.debug(tables)

    output = gen_drawing(tables)
    logging.debug(output_filename)

    save_drawing(output, output_filename)
    open_drawing(output_filename)
