import sqlparse
from sql_metadata import Parser
import json
import os

print('parse loaded')

def main(path):

    with open(path, 'r') as f:
        raw = f.read()

    statements = sqlparse.parse(raw)

    for stat in statements:
        if stat.get_type() == 'CREATE':

            for line in str(stat).split('\n'):
                if ('CREATE TABLE' in line) and ('AS' in line):
                    l = line.split(' ')
                    target_table = l[2]
                elif 'INSERT INTO' in line:
                    l = line.split(' ')
                    target_table = l[2]
                
            split = str(stat).replace('\n',' ').split(' ')
            split = list(filter(None, split))

            print(split)
            res_list = [i for i, value in enumerate(split) if value == 'FROM']
            if len(res_list) != 0:
                source_table = split[res_list[-1]+1] 
                print('SOURCE TABLE:', source_table, '\n')  
    


            print('TARGET TABLE:', target_table, '\n')

            # print('\n'*3, stat, '\n')
            p = Parser(str(stat))
            # print('Columns', p.columns_dict, '\n')
            # print('Aliases', p.columns_aliases, '\n')
            # print('Tables', p.tables, '\n')
    
            # All the alias cols
            # Therefore those that are additional (so completely new)
            alias_cols = []
            if p.columns_aliases_dict != None:
                for alias in p.columns_aliases_dict['select']:
                    alias_cols.append(alias)
                print('ALIAS COLS:', alias_cols, '\n')

            # All the source cols
            # Therefore all of these should be in the target table
            # With the except of those that are used to create an alias
            source_cols = []
            for source_col in p.columns_dict['select']:
                source_cols.append(source_col)
            print('SOURCE COLS:', source_cols, '\n')

            # All the source cols that are used to create an alias
            # Therefore these should not be in the target table
            # (But there is a gap here - some cols might be used to create
            # an alias AND be in the target table)
            source_cols_for_alias = []
            for alias in p.columns_aliases:
                # print(alias, p.columns_aliases[alias], type(p.columns_aliases[alias]))
                # p.columns_aliases[alias] is either string or "UniqueList" class
                # depending on if there are multiple source columns
                if isinstance(p.columns_aliases[alias], str):
                    source_cols_for_alias.append(p.columns_aliases[alias])
                else:
                    for source_col in p.columns_aliases[alias]:
                        source_cols_for_alias.append(source_col) 
            print('SOURCE COLS FOR ALIAS:', source_cols_for_alias, '\n')

            
            
            # Target cols is all the cols in source, minus the ones used to
            # create an alias (this logic needs work!)
            target_cols = list(set(alias_cols)-set(source_cols)) + list(set(source_cols)-set(source_cols_for_alias))

            # Corrector function for the above loophole
            # Works by looping through all the source_cols that are used to create an alias
            # Then looks through the whole script, picking out lines where the source_col features
            # Then checks to see that the mention of this source_col, is the LAST mention in the line
            # (And therefore actually the name of the col being pulled through to the target table)
            # If so it adds it back to target_cols so it is still captured        
            for col in source_cols_for_alias:
                col_name = col.split('.')[-1]
                for line in str(stat).split('\n'):
                    # print(line)
                    if col_name in line:
                        split_line = line.replace('.',' ').replace(',','').split(' ')
                        # print(col_name, split_line)
                        res_list = [i for i, value in enumerate(split_line) if value == col_name]

                        if len(res_list) != 0:
                            # print(col_name, split_line)
                            # print(res_list[-1])
                            # print(split_line, res_list[-1], len(split_line)-1)

                            if res_list[-1] == len(split_line)-1:
                                target_cols.append(col)


            cols = {}

            print('P COLUMNS ALIASES:', p.columns_aliases, '\n')

            print('TARGET COLS:', target_cols, '\n')

            for col in target_cols:
                if col in p.columns_aliases:
                    target_col_name = target_table + '.' + col
                    if len(p.columns_aliases[col]) != 0:
                        if isinstance(p.columns_aliases[col], list):
                            cols[target_col_name] = p.columns_aliases[col]
                        else:
                            cols[target_col_name] = [p.columns_aliases[col]]

                else:
                    target_col_name = target_table + '.' + col.split('.')[-1]
                    
                    if '.' not in col:
                        source_col_name = source_table + '.' + col
                        cols[target_col_name] = [source_col_name]
                        print('DEBUGGING2', [source_col_name])


                    else:
                        cols[target_col_name] = [col]
                        print('DEBUGGING3', [col])


            output_folder = '../working-files'
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            output_fn = output_folder + '/' + target_table + '.json'

            with open(output_fn, "w") as f:
                json.dump(cols, f, indent=6)