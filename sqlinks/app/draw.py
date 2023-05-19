"""draw.py."""
from jinja2 import Environment, FileSystemLoader
import logging
from pathlib import Path
import os


def gen_drawing(snapshot):
    """_summary_
    Args:
        tables (_type_): _description_

    Returns:
        _type_: _description_
    """
    file_loader = FileSystemLoader(Path(__file__).parent / "templates/")
    env = Environment(loader=file_loader)

    template = env.get_template("drawio_template.xml")

    output = template.render(snapshot=snapshot)
    return output


def save_drawing(output, output_filename):
    """_summary_
    Args:
        output (_type_): _description_
        output_filename (_type_): _description_
    """
    with open(output_filename, "w+") as f:
        f.write(output)


def save_drawing(output, output_filename):
    """_summary_

    Args:
        output (_type_): _description_
        output_filename (_type_): _description_
    """
    with open(output_filename, "w+") as f:
        f.write(output)


def main(collection, output_filename: Path):
    """_summary_

    Args:
        working_dir (Path): _description_
        output_filename (Path): _description_
    """

    output = gen_drawing(snapshot=collection.snapshot)
    logging.debug(output_filename)

    save_drawing(output, output_filename)
