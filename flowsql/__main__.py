import argparse

import flowsql.app.parse as parse
import flowsql.app.populate as populate
import flowsql.app.draw as draw
import flowsql.app.scan as scan

print('program started')

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", default='.', help="Path to scan across | Default value = .")
parser.add_argument("-o", "--output", default='.', help="Path to output diagrams | Set to 'REL' to save adjacent to scripts | Default value = .")
args = parser.parse_args()

print(__name__)
if __name__ == '__main__':
    paths = scan.main(args.path)
    for path in paths:
        parse.main(path)
        populate.main()
        draw.main(args.output)
        exit()