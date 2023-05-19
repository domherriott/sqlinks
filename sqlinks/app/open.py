import os
import logging


def open_drawing(output_filename):
    """_summary_
    Args:
        output_filename (_type_): _description_
    """
    try:
        os.system("open {}".format(output_filename))
    except:
        logging.error("Unable to open .drawio file")
