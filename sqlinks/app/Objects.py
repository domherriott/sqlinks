import pprint
import math
from sqlinks.app.helpers import deconstruct_sid


class Object:
    object_counter = 1000

    def __init__(self, sid):
        # String ID
        self.sid = sid
        # Numerical ID
        self.nid = Object.object_counter
        Object.object_counter += 1


class Schema(Object):
    def __init__(self, sid: str):
        Object.__init__(self, sid)
        self.name = sid
        self.tables = {}

        # Aggregates to be calculated later on
        self._num_tables = 0
        self._num_children = 0
        self._num_parents = 0
        self._order = None

    def add_table(self, sid: str, schema_sid: int):
        if sid in self.tables:
            return

        self.tables[sid] = Table(sid=sid, schema_sid=schema_sid)


class Table(Object):
    def __init__(self, sid: str, schema_sid: str):
        Object.__init__(self, sid)
        self.schema_sid = schema_sid
        self.name = sid.split(".")[1]
        self.max_text_length = len(self.name)

        self.columns = {}

        # Aggregates to be calculated later on
        self._num_columns = 0
        self._num_children = 0
        self._num_parents = 0
        self._order = None

    def add_column(self, sid: str, table_sid: int):
        if sid in self.columns:
            return

        new_column = Column(sid=sid, table_sid=table_sid)
        self.columns[sid] = new_column

        column_name_len = len(sid.split(".")[2])
        if column_name_len > self.max_text_length:
            self.max_text_length = column_name_len


class Column(Object):
    def __init__(self, sid: str, table_sid: str):
        Object.__init__(self, sid)
        self.table_sid = table_sid
        self.name = sid.split(".")[2]

        # Links are associated by the target column
        self.links = {}

    def add_link(self, source_col_sid: int, target_col_sid: int):
        new_link = Link(source_col_sid=source_col_sid, target_col_sid=target_col_sid)
        self.links[new_link.nid] = new_link


class Link(Object):
    def __init__(self, source_col_sid: str, target_col_sid: str):
        Object.__init__(self, sid=None)
        self.source_sid = source_col_sid
        self.target_sid = target_col_sid


class Collection:
    def __init__(self):
        self.schemas = {}

    def add_schema(self, sid: str):
        print(sid, self.schemas)
        if sid in self.schemas:
            return
        self.schemas[sid] = Schema(sid=sid)

    def get_object(self, sid: str):
        dot_count = sid.count(".")

        if dot_count == 0:
            try:
                object = self.schemas[sid]
            except:
                return None

        elif dot_count == 1:
            schema, table = deconstruct_sid(sid, how="table")
            try:
                object = self.schemas[schema].tables[table]
            except:
                return None

        elif dot_count == 2:
            schema, table, column = deconstruct_sid(sid, how="column")
            try:
                object = self.schemas[schema].tables[table].columns[column]
            except:
                return None

        return object

    def calculate_aggregates(self):

        # Calculating these aggregates for both Schema & Table
        #
        # self._num_columns = None
        # self._num_children = None
        # self._num_parents = None
        # self._order = None
        #

        # First we must calculate _num_columns, _num_children, _num_parents
        # Which then allows _order to be determined
        for schema_sid, schema in self.schemas.items():
            schema._num_tables = len(schema.tables)
            schema._max_num_columns = 0

            for table_sid, table in schema.tables.items():
                table._num_columns = len(table.columns)
                if table._num_columns > schema._max_num_columns:
                    schema._max_num_columns = table._num_columns

                for column_sid, column in table.columns.items():

                    for link_nid, link in column.links.items():
                        source_schema, source_table, source_column = deconstruct_sid(
                            column_sid, how="column"
                        )
                        target_schema, target_table, target_column = deconstruct_sid(
                            column_sid, how="column"
                        )

                        self.schemas[source_schema]._num_children += 1
                        self.schemas[source_schema].tables[
                            source_table
                        ]._num_children += 1

                        self.schemas[target_schema]._num_parents += 1
                        self.schemas[target_schema].tables[
                            target_table
                        ]._num_parents += 1

        # Calculate secondary aggregates
        for schema_sid, schema in self.schemas.items():

            for table_sid, table in schema.tables.items():
                table._net_parent = table._num_parents - table._num_children

            schema._net_parent = schema._num_parents - schema._num_children

        # Table ordering
        for schema_sid, schema in self.schemas.items():
            sorted_tables = sorted(
                schema.tables.items(), key=lambda x: x[1]._net_parent, reverse=True
            )

            for i in range(0, len(sorted_tables)):
                table_sid = sorted_tables[i][0]
                schema.tables[table_sid]._order = i + 1

        # Schema ordering
        sorted_schemas = sorted(
            self.schemas.items(), key=lambda x: x[1]._net_parent, reverse=True
        )

        for i in range(0, len(sorted_schemas)):
            schema_sid = sorted_schemas[i][0]
            self.schemas[schema_sid]._order = i + 1

    def print_snapshot(self, how="pretty"):
        def pretty_print_snapshot(snapshot=self.snapshot):

            line_breaks = 3
            schema_offset = 2
            table_offset = 3
            whole_line = 100
            column_width = (whole_line - table_offset) // 2

            def print_line(type=None, text="", source_sid=None, target_sid=None):

                if type == "schema":
                    print("\n" * line_breaks)
                    print(" " * schema_offset + "#" * whole_line)
                    buffer = 3
                    offset = len(text) // 2
                    print(" " * schema_offset + " " * (column_width - offset) + text)
                    print(" " * schema_offset + "#" * whole_line)

                elif type == "table":
                    print()
                    print(" " * table_offset + "+" + "-" * column_width * 2 + "+")
                    offset = len(text) // 2
                    print(
                        " " * table_offset
                        + "|"
                        + " " * (column_width - offset)
                        + text
                        + " " * (column_width - (len(text) - offset))
                        + "|"
                    )
                    print(" " * table_offset + "+" + "-" * column_width * 2 + "+")

                elif type == "link":
                    print(
                        " " * table_offset
                        + "|"
                        + source_sid
                        + " " * (column_width - len(source_sid) - 2)
                        + "->"
                        + " " * (column_width - len(target_sid))
                        + target_sid
                        + "|"
                    )
                    print(" " * table_offset + "+" + "-" * column_width * 2 + "+")

            for schema in snapshot:
                schema_sid = schema["name"]
                print_line(type="schema", text=schema_sid)

                for table in schema["tables"]:
                    table_sid = table["name"]
                    print_line(type="table", text=table_sid)

                    for column in table["cols"]:
                        column_sid = column["name"]

                        links = column["links"]

                        if links == []:
                            print_line(
                                type="link", source_sid="", target_sid=column_sid
                            )

                        else:
                            for link in links:
                                print_line(
                                    type="link",
                                    source_sid=link["source_sid"],
                                    target_sid=link["target_sid"],
                                )

            print("\n" * line_breaks)

        if how == "raw":
            pprint.pprint(self.snapshot)
        elif how == "pretty":
            pretty_print_snapshot()

    def create_snapshot(self):
        """
        snapshot is the desired end state. This is what is used as an input to Jinja to create the
        draw.io diagram.
        snapshot = [
            {
                'name':'stage.reference_rts',
                'id':3,
                'x':900,
                'cols':[
                    {
                        'name':'region',
                        'id':301,
                        'y':26,
                        'links':[]
                    },
                    {
                        'name':'county',
                        'id':302,
                        'y':52,
                        'links':[{
                                'link_id':900,
                                'parent_id':402
                            }]
                    },
                    {
                        'name':'indoor_outdoor',
                        'id':303,
                        'y':78,
                        'links':[]
                    }
                ]
            },
            {
                'name':'reporting.reference_postcode',
                'id':4,
                'x': 300,
                'cols':[
                    {
                        'name':'region_name',
                        'id':401,
                        'y':26,
                        'links':[]
                    },
                    {
                        'name':'county_name',
                        'id':402,
                        'y':52,
                        'links':[]
                    }
                ]
            }
        ]
        """

        def create_snapshot():
            snapshot = []

            row_height = 26
            width_per_char = 8

            schema_int_buffer = 50
            schema_buffer = 500

            for schema_sid, schema in self.schemas.items():
                schema = self.schemas[schema_sid]

                tables_per_column = max(2, schema._num_tables // 2)
                table_x_buffer = 700
                table_y_buffer = 50 + (schema._max_num_columns + 1) * row_height

                schema_x = (schema._order - 1) * schema_buffer

                schema_y = 0

                number_of_columns = math.ceil(schema._num_tables / tables_per_column)
                schema_width = 350 + (number_of_columns - 1) * table_x_buffer
                schema_height = schema_int_buffer + (tables_per_column) * table_y_buffer

                schema_snapshot = {
                    "name": schema.sid,
                    "id": schema.nid,
                    "x": schema_x,
                    "y": schema_y,
                    "height": schema_height,
                    "width": schema_width,
                    "color": "#FFFFFF",
                    "tables": [],
                }

                for table_sid, table in schema.tables.items():
                    table_width = table.max_text_length * width_per_char

                    table_snapshot = {
                        "name": table.name,
                        "id": table.nid,
                        "order": table._order,
                        "height": (table._num_columns + 1) * row_height,
                        "width": table_width,
                        "x": schema_int_buffer
                        + ((table._order - 1) // tables_per_column) * table_x_buffer,
                        "y": schema_int_buffer
                        + ((table._order - 1) % tables_per_column) * table_y_buffer,
                        "color": "#FFFFFF",
                        "cols": [],
                    }

                    column_counter = 1
                    link_counter = 1

                    for column_sid, column in table.columns.items():

                        column_snapshot = {
                            "name": column.name,
                            "id": column.nid,
                            "width": table_snapshot["width"],
                            "height": row_height,
                            "y": column_counter * row_height,
                            "color": "#FFFFFF",
                            "links": [],
                        }

                        for link_nid, link in column.links.items():
                            link_snapshot = {
                                "link_id": link_nid,
                                "parent_id": self.get_object(link.source_sid).nid,
                                "mx": schema_snapshot["x"]
                                + table_snapshot["x"]
                                - (300 // table._num_columns) * link_counter,
                                "my": schema_snapshot["y"]
                                + table_snapshot["y"]
                                + column_snapshot["y"],
                                "source_sid": link.source_sid,
                                "target_sid": link.target_sid,
                            }
                            column_snapshot["links"].append(link_snapshot)
                            link_counter += 1

                        table_snapshot["cols"].append(column_snapshot)
                        column_counter += 1

                    schema_snapshot["tables"].append(table_snapshot)

                snapshot.append(schema_snapshot)

            return snapshot

        self.calculate_aggregates()
        self.snapshot = create_snapshot()
        self.print_snapshot(how="raw")
        self.print_snapshot(how="pretty")
