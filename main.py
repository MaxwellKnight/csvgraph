from csvgraph import *
from sqlparser import SQLParser

# List of tables with filenames and their corresponding indexes
filtered = [
    'nibrs_offense', 
    'nibrs_offender',
    'nibrs_incident',
    'nibrs_victim',
    'nibrs_victim_injury',
    'nibrs_victim_offender_rel',
    'nibrs_weapon',
    'nibrs_weapon_type',
    'nibrs_victim_type',
]

def create_graph(tables, foreign_keys):
    nodes = {}
    graph = CSVGraph()

    # Create nodes for each filtered table with numerical labels
    for index, table_name in enumerate(filtered):
        if table_name in tables:
            node = CSVNode(index + 1, tables[table_name])
            nodes[table_name] = node
            graph.nodes.append(node)

    # Add edges based on foreign key relationships
    for table, fks in foreign_keys.items():
        table = table.lower()  
        if table not in nodes:
            continue

        for fk in fks:
            ref_table = fk['ref_table'].lower()
            if ref_table not in nodes:
                continue

            left_node = nodes[table]
            right_node = nodes[ref_table]
            columns = fk['columns']
            graph.add_edge(CSVEdge(left_node, right_node, columns))

    return graph

if __name__ == "__main__":
    sql_file_path = 'postgres_setup.sql'
    with open(sql_file_path, 'r') as file:
        sql_content = file.read()

    parser = SQLParser(sql_content)
    tables, primary_keys, foreign_keys = parser.parse()
    filtered_parsed_tables = {k: v for k, v in tables.items() if k.lower() in tables}

    graph = create_graph(filtered_parsed_tables, foreign_keys)
    graph.compress_graph()
    visualize(graph)
