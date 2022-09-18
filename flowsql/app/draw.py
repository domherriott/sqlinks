import pickle
from jinja2 import Environment, FileSystemLoader
import os

def gen_drawing(tables):
    file_loader = FileSystemLoader('flowsql/app/templates')
    env = Environment(loader=file_loader)

    template = env.get_template('drawio_template_2.xml')

    output = template.render(tables=tables)
    return output


def save_drawing(output, output_filename):
    with open(output_filename, 'w+') as f:
        f.write(output)


def open_drawing(output_filename):
    try:
        os.system("open {}".format(output_filename))
    except:
        print('unable to open .drawio file')


def main(output_location):

    #reload object from file
    with open(r'./working-files/tables.pkl', 'rb') as f:
        tables = pickle.load(f)


    print(tables)

    output = gen_drawing(tables)
    output_filename = output_location + '/output.drawio'
    print(output_filename)

    save_drawing(output, output_filename)
    open_drawing(output_filename)