from jinja2 import Environment, FileSystemLoader
import json
import os

master_mapping = {}

# to be looped over all files
for filename in os.listdir('../working-files'):
    if filename[0] == '.':
        pass
    else:
        print(filename)
        with open('../working-files/'+filename) as f:
            mapping = json.loads(f.read())

        master_mapping.update(mapping)

        master_all_cols_raw = []

        for target_col in master_mapping:
            master_all_cols_raw.append(target_col)
            
            value = master_mapping[target_col] 

            for source_col in value:
                master_all_cols_raw.append(source_col)
            
            # if isinstance(value, list):
            #     for source_col in value:
            #         master_all_cols_raw.append(source_col)
            # else:
            #     master_all_cols_raw.append(value)

# print(master_all_cols_raw)


# Dictionary of all tables with a list of all columns
master_all_cols = {}

for col in master_all_cols_raw:
    t, c = col.rsplit('.', 1)
    if t in master_all_cols:
        if c in master_all_cols[t]:
            pass
        else:
            master_all_cols[t].append(c)
    else:
        master_all_cols[t] = [c]



# print(master_all_cols)


# Dicitonary of all target columns with a list of source columns
# print(master_mapping)

starting_counter = 100
id_counter = starting_counter + 1

table_counter = 1
x_delta = 300

tables = []

for table in master_all_cols:

    table_dict = {
        'name': table,
        'id': id_counter,
        'x': None,
        'y': None,
        'height': None,
        'width': 200,
        'cols': None,
        'number_of_parents': 0,
        'number_of_children': 0
    }
    id_counter += 1


    cols = []

    y_delta = 26 
    col_counter = 1

    for col in master_all_cols[table]:
        # print(col)

        cols.append({
            'name':col,
            'id':id_counter,
            'y':col_counter * y_delta,
            'links':None
        })

        id_counter += 1
        col_counter += 1


    table_dict['cols'] = cols
    tables.append(table_dict)
    table_counter += 1

# print(master_mapping)

id_col_lookup = {}
for table in tables:
    for col in table['cols']:
        id_col_lookup[table['name'] + '.' + col['name']] = col['id']

row_height = 26

for table in tables:
    table_link_number = 1
    table['height'] = (len(table['cols'])+1) * row_height
    
    for col in table['cols']:
        full_name = table['name'] + '.' + col['name']
        links = []

        if full_name in master_mapping:
            parent_cols = master_mapping[full_name]
            for parent_col in parent_cols:
                links.append({
                    'link_id': id_counter,
                    'parent_id': id_col_lookup[parent_col],
                    'mx': None,
                    'my': None,
                    'table_link_number': table_link_number
                })
                id_counter += 1
                table_link_number += 1
                table['number_of_parents'] += 1

                for table2 in tables:
                    for col2 in table2['cols']:
                        # print(col2['id'])
                        if col2['id'] == id_col_lookup[parent_col]:
                            # print('child')
                            table2['number_of_children'] += 1
                        else:
                            pass
        col['links'] = links


ordering_dict = {}

for table in tables:
    ordering_dict[table['name']] = {
        'number_of_parents':table['number_of_parents'],
        'number_of_children':table['number_of_children']
    }


# sort by awayPoints, then position; note the lambda uses a tuple
order = 0
ordering = {}
for table in sorted(ordering_dict, key = lambda k: (ordering_dict[k]['number_of_parents'], -ordering_dict[k]['number_of_children'])):
    ordering[table] = order
    order += 1
    


# order = 1
# ordering = {}
# for table in ordering_dict:
#     ordering[table] = order
#     order += 1

x_delta = 400
y_delta = 200
for table in tables:
    table['x'] = x_delta + (ordering[table['name']] * x_delta)
    table['y'] = y_delta + ((ordering[table['name']] % 4) * y_delta)
    print(ordering[table['name']]%4+1)

    for col in table['cols']:
        for link in col['links']:
            link['mx'] = table['x'] - (link['table_link_number'] * 26)
            link['my'] = table['y'] + col['y']


# print(number_of_parents)

print(tables)


# tables is the desired end state
# tables = [
#     {
#         'name':'stage.reference_rts',
#         'id':3,
#         'x':900,
#         'cols':[
#             {
#                 'name':'region',
#                 'id':301,
#                 'y':26,
#                 'links':[]
#             },
#             {
#                 'name':'county',
#                 'id':302,
#                 'y':52,
#                 'links':[{
#                         'link_id':900,
#                         'parent_id':402
#                     }]
#             },
#             {
#                 'name':'indoor_outdoor',
#                 'id':303,
#                 'y':78,
#                 'links':[]
#             }
#         ]
#     },
#     {
#         'name':'reporting.reference_postcode',
#         'id':4,
#         'x': 300,
#         'cols':[
#             {
#                 'name':'region_name',
#                 'id':401,
#                 'y':26,
#                 'links':[]
#             },
#             {
#                 'name':'county_name',
#                 'id':402,
#                 'y':52,
#                 'links':[]
#             }
#         ] 
#     }
# ]

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

template = env.get_template('drawio_template.xml')

output = template.render(tables=tables)


with open('../outputs/output.drawio', 'w+') as f:
    f.write(output)

# print(output)