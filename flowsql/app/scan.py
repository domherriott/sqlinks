import os


def main(path):
    paths = []

    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            if name.lower().endswith("sql"):
                relative_path = os.path.join(dirpath, name)
                absolute_path = os.path.abspath(relative_path)
                paths.append(absolute_path)

    return paths
