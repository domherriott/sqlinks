import sqlparse
from sql_metadata import Parser
import json
import os
import logging
import itertools


class ObjectCollection:
    def __init__(self):
        self._schemas = []
        self._schema_lookup = {}
        self._tables = []
        self._table_lookup = {}
        self._columns = []
        self._column_lookup = {}
        self._links = []

    def add_schema(self, name: str):
        print(name, self._schema_lookup)
        if name in self._schema_lookup:
            return
        new_schema = Schema(name=name)
        self._schemas.append(new_schema)
        self._schema_lookup[new_schema.name] = new_schema.id

    def add_table(self, name: str, schema_id: int):
        if name in self._table_lookup:
            return
        new_table = Table(name=name, schema_id=schema_id)
        self._tables.append(new_table)
        self._table_lookup[new_table.name] = new_table.id

    def add_column(self, name: str, table_id: int):
        if name in self._column_lookup:
            return
        new_column = Column(name=name, table_id=table_id)
        self._columns.append(new_column)
        self._column_lookup[new_column.name] = new_column.id

    def add_link(self, source_col_id: int, target_col_id: int):
        new_link = Link(source_col_id=source_col_id, target_col_id=target_col_id)
        self._links.append(new_link)


class Object:
    object_counter = 1

    def __init__(self, name):
        self.name = name
        self.id = Object.object_counter
        Object.object_counter += 1


class Schema(Object):
    def __init__(self, name: str):
        Object.__init__(self, name)
        self.name = name


class Table(Object):
    def __init__(self, name: str, schema_id: str):
        Object.__init__(self, name)
        self.schema_id = schema_id


class Column(Object):
    def __init__(self, name: str, table_id: str):
        Object.__init__(self, name)
        self.table_id = table_id


class Link(Object):
    def __init__(self, source_col_id: int, target_col_id: int):
        Object.__init__(self, name=None)
        self.source_id = source_col_id
        self.target_id = target_col_id


def parse_create_statement(collection: ObjectCollection, statement):
    def get_target_table(statement):
        for line in str(statement).split("\n"):
            if ("CREATE TABLE" in line) and ("AS" in line):
                l = line.split(" ")
                target = l[2]
            elif "INSERT INTO" in line:
                l = line.split(" ")
                target = l[2]

        target_schema, target_table = target.split(".")

        return target_schema, target_table

    def get_cols_and_links(parser, target_schema: str, target_table: str):

        # Source cols =
        #  Any column named in the parser.columns attribute
        source_cols = parser.columns

        # Target cols =
        #  Any column named in the parser.columns attribute (remapped to the target table)
        #  Remapped using the parser.columns_aliases attribute
        #  You must then add again any duplicated source columns that this time DON'T have an alias.
        #
        #  e.g. In this example c.country is picked up as a source column but only once.
        #       Therefore overlaying the parser.columns_aliases will leave us without a "country"
        #       column in the target (only "country_2") unless a corrector function is applied.
        #         SELECT
        #             c.id,
        #             c.name as name,
        #             c.age_int as age,
        #             c.country as country_2,
        #             c.country
        #         FROM spectrum.customers c;

        # Aliases is a lookup of target alias -> source
        aliases = parser.columns_aliases

        # Invert aliases to act as a lookup of source -> target
        inv_aliases = {v: k for k, v in aliases.items()}

        # Create a list of target cols (excl. schema + table)
        # Replaces source col with alias if present, otherwise takes the source col name
        target_cols = []
        links = []
        for source_col in source_cols:
            if source_col in inv_aliases:
                # Add schema and table info to target cols
                target_col = f"{target_schema}.{target_table}.{inv_aliases[source_col]}"
                target_cols.append(target_col)

            else:
                # Add schema and table info to target cols
                target_col = (
                    f'{target_schema}.{target_table}.{source_col.split(".")[2]}'
                )
                target_cols.append(target_col)

            # Add links for aliases and non-aliased cols
            links.append([source_col, target_col])

        all_cols = source_cols + target_cols

        return all_cols, links

        # # Corrector function for the above loophole
        # # Works by looping through all the source_cols that are used to create an alias
        # # Then looks through the whole script, picking out lines where the source_col features
        # # Then checks to see that the mention of this source_col, is the LAST mention in the line
        # # (And therefore actually the name of the col being pulled through to the target table)
        # # If so it adds it back to target_cols so it is still captured
        # for col in source_cols_for_alias:
        #     col_name = col.split(".")[-1]
        #     for line in str(statement).split("\n"):
        #         if col_name in line:
        #             split_line = line.replace(".", " ").replace(",", "").split(" ")
        #             res_list = [
        #                 i for i, value in enumerate(split_line) if value == col_name
        #             ]

        #             if len(res_list) != 0:
        #                 if res_list[-1] == len(split_line) - 1:
        #                     target_cols.append(col)

    target_schema, target_table = get_target_table(statement=statement)
    parser = Parser(str(statement))

    all_cols, links = get_cols_and_links(
        parser=parser, target_schema=target_schema, target_table=target_table
    )

    for col in all_cols:
        schema, table = col.split(".")[:2]
        collection.add_schema(name=schema)

        schema_id = collection._schema_lookup[schema]
        collection.add_table(name=table, schema_id=schema_id)

        table_id = collection._table_lookup[table]
        collection.add_column(name=col, table_id=table_id)

    for link in links:
        source_col_id = collection._column_lookup[link[0]]
        target_col_id = collection._column_lookup[link[1]]

        collection.add_link(source_col_id=source_col_id, target_col_id=target_col_id)

    return collection


# def clean(statement):
#     """
#     Clean the statement, returning a list of individual words.

#     Args:
#         statement (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     # # Remove new lines to negate different formats
#     # statement = str(statement).replace('\n', ' ')
#     # # Remove semi-colons as they mark the end of SQL statements
#     # statement = str(statement).replace(';', '')

#     # statement = statement.split(' ')
#     # statement = [s for s in statement if s != '']
#     return statement


def create_collection(statements):

    collection = ObjectCollection()

    # Looping through all SQL statements in the file, determine what type of statement it is. Add to mapping file accordingly.
    for statement in statements:
        statement_type = statement.get_type()
        # statement = clean(statement)

        if statement_type == "CREATE":
            mapping = parse_create_statement(collection=collection, statement=statement)

        # TODO: Insert other SQL statements here...

    return mapping


def main(path):

    with open(path, "r") as f:
        raw = f.read()

    statements = sqlparse.parse(raw)

    collection = create_collection(statements=statements)

    # output_folder = "working-files"
    # if not os.path.exists(output_folder):
    #     os.makedirs(output_folder)

    # with open('output.json', "w") as f:
    #     json.dump(mappings, f, indent=6)
