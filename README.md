# CSV Graph Visualization from SQL Schema

This project parses an SQL schema to extract table definitions, primary keys, and foreign keys, and then visualizes the relationships between tables as a graph. The nodes in the graph represent tables, and the edges represent foreign key relationships.

## Features

- **SQL Parsing**: Extracts table definitions, primary keys, and foreign keys from an SQL file.
- **Graph Construction**: Creates a graph where nodes represent tables and edges represent foreign key relationships.
- **Graph Compression**: Compresses paths in the graph to create direct edges between related tables.
- **Visualization**: Visualizes the graph using NetworkX and Matplotlib.

## Project Structure

- `csvgraph.py`: Contains the classes and functions for representing and manipulating the graph structure.
- `sqlparser.py`: Contains the `SQLParser` class for parsing SQL content and extracting table and key information.
- `main.py`: The main script that integrates the SQL parser with the graph creation and visualization.
- `tests.py`: Contains unit tests for the `SQLParser` class to ensure correct parsing of SQL schema.

## Usage

### Prerequisites

Make sure you have Python installed, along with the following libraries:

- `networkx`
- `matplotlib`

You can install the dependencies using pip:

```bash
pip install networkx matplotlib
```

## Running the Project

1. Prepare Your SQL File: Place your SQL schema file in the project directory. The script assumes the file is named `postgres_setup.sql`, but you can change the filename in the script.

2. Run the Script:

```bash
python main.py
```

This will:
- Parse the SQL schema.
- Create a graph based on the filtered tables and foreign key relationships.
- Compress the graph by adding direct edges between related tables.
- Visualize the graph.

## Running Tests

The project includes unit tests for the SQLParser class, which are currently not passing because the current SQL parsing approach based on regex is insufficient for some complex SQL syntax. A more robust SQL parsing solution is needed.

To run the tests:

```bash
python -m unittest tests.py
```

The tests cover various scenarios including:

- Composite primary keys
- Primary keys in `ALTER TABLE` statements
- Complex column definitions
- Quoted identifiers and mixed case
- Foreign keys with multiple columns
- Foreign keys with schema prefixes
- Constraints in multiple statements
- SQL syntax variations

## Example

If you have an SQL schema with the following tables and relationships:

- `nibrs_offense` (`Primary key`: offense_id)
- `nibrs_offender` (`Primary key`: offender_id, `Foreign key`: incident_id references nibrs_incident)
- `nibrs_incident` (`Primary key`: incident_id)
- `nibrs_victim` (`Primary key`: victim_id, `Foreign key`: incident_id references nibrs_incident)

The script will create and visualize a graph where each table is a node, and the foreign key relationships are edges between nodes.
