import re
from collections import defaultdict

class SQLParser:
    def __init__(self, sql_content):
        self.sql_content = sql_content
        self.tables = defaultdict() 
        self.primary_keys = defaultdict(list)
        self.foreign_keys = defaultdict(list)
        self._compile_patterns()

    def _compile_patterns(self):
        self.create_table_pattern = re.compile(r'CREATE TABLE (\w+)\s*\((.*?)\);', re.S)
        self.primary_key_pattern = re.compile(r'PRIMARY KEY\s*\((.*?)\)', re.S)
        self.alter_table_pk_pattern = re.compile(
            r"ALTER TABLE ONLY\s+(?:PUBLIC\.)?(\S+)\s+ADD CONSTRAINT \S+ PRIMARY KEY \((.*?)\);", re.S
        )
        self.foreign_key_pattern = re.compile(
            r"ALTER TABLE ONLY\s+(?:PUBLIC\.)?(\S+)\s+ADD CONSTRAINT \S+\s+FOREIGN KEY \(([^)]+)\)\s+"
            r"REFERENCES\s+(?:PUBLIC\.)?(\S+)\s+\(([^)]+)\)", re.S
        )

    def parse(self):
        self._parse_create_table_statements()
        self._parse_primary_keys()
        self._parse_alter_table_primary_keys()
        self._parse_foreign_keys()

        return self.tables, self.primary_keys, self.foreign_keys

    def _parse_create_table_statements(self):
        for match in self.create_table_pattern.finditer(self.sql_content):
            table_name = match.group(1)
            columns = match.group(2)
            columns = [col.strip().split()[0] for col in columns.split(',')]
            self.tables[table_name] = columns

    def _parse_primary_keys(self):
        for table_name, columns in self.tables.items():
            column_definitions = ','.join(columns)
            pk_match = self.primary_key_pattern.search(column_definitions)
            if pk_match:
                pk_columns = pk_match.group(1).split(',')
                self.primary_keys[table_name].extend([col.strip().lower() for col in pk_columns])

    def _parse_alter_table_primary_keys(self):
        for match in self.alter_table_pk_pattern.finditer(self.sql_content):
            table_name = match.group(1)
            pk_columns = match.group(2).split(',')
            self.primary_keys[table_name].extend([col.strip().lower() for col in pk_columns])

    def _parse_foreign_keys(self):
        for match in self.foreign_key_pattern.finditer(self.sql_content):
            table_name = match.group(1)
            fk_columns = match.group(2).split(',')
            ref_table = match.group(3)
            ref_columns = match.group(4).split(',')
            self.foreign_keys[table_name].append({
                'columns': [col.strip().lower() for col in fk_columns],
                'ref_table': ref_table.lower(),
                'ref_columns': [col.strip().lower() for col in ref_columns]
            })
