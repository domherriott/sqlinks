import graphviz  
import os
import json


s = graphviz.Digraph('structs', 
                    filename='structs_revisited.gv',
                    engine='circo',
                    graph_attr={'rankdir':'LR'},
                    node_attr={'shape': 'record'})


fn = 'doctest-output/round-table.gv'

master_mapping = {}

# to be looped over all files
for filename in os.listdir('json_mappings'):

    with open('json_mappings/'+filename) as f:
        mapping = json.loads(f.read())

    master_mapping.update(mapping)

    master_all_cols_raw = []

    for target_col in master_mapping:
        master_all_cols_raw.append(target_col)
        
        value = master_mapping[target_col] 
        if isinstance(value, list):
            for source_col in value:
                master_all_cols_raw.append(source_col)
        else:
            master_all_cols_raw.append(value)

# print(master_all_cols_raw)

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

print(master_all_cols)



for t in master_all_cols:

    table_dot = ''

    for c in master_all_cols[t]:
        # uid = t + '.' + c
        # print(c)
        table_dot += '<port_{}>'.format(c) + c + ' | '

    struct_name = 'struct_{}'.format(t)
    table_dot = ' |{| ' + t + ' |}| |' + table_dot[:-3] + ' '

    schema = t.split('.',1)[0]
    if schema == 'prod_redshift_jdbc':
        schema_rank = 'min'
    elif schema == 'stage':
        schema_rank = 'same'
    elif schema == 'reporting':
        schema_rank = 'max'
    else:
        schema_rank = 'same'
        
    s.attr(rank=schema_rank)
    s.node(struct_name, table_dot)

edges_list = []
print(master_mapping)
for target_col in master_mapping:
    target_t, target_c = target_col.rsplit('.', 1)
    target_struct = 'struct_{}'.format(target_t)
    target_port = 'port_{}'.format(target_c)

    value = master_mapping[target_col]
    if isinstance(value, list):
        if len(value) > 0:
            for source_col in value:
                print(source_col)
    else:
        source_col = value
        source_t, source_c = source_col.rsplit('.', 1)
        source_struct = 'struct_{}'.format(source_t)
        source_port = 'port_{}'.format(source_c)

        edges_list.append((source_struct+':'+source_port, target_struct+':'+target_port))
        
# print(edges_list)
s.edges(edges_list)


s.render(directory='doctest-output', view=True)  
