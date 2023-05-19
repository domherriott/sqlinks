import os
from pathlib import Path


def main(path):
    """
    For the provided path, return list of all SQL files
    """
    paths = []

    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            if name.lower().endswith("sql"):
                relative_path = os.path.join(dirpath, name)
                absolute_path = os.path.abspath(relative_path)
                paths.append(
                    {
                        "absolute_path": Path(absolute_path),
                        "relative_path": Path(relative_path),
                    }
                )

    return paths
