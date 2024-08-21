import unittest
from sqlparser import SQLParser

class TestSQLParser(unittest.TestCase):

    def run_parser(self, sql_content):
        parser = SQLParser(sql_content)
        return parser.parse()

    def test_composite_primary_key(self):
        sql_content = '''
        CREATE TABLE orders (
            order_id INT,
            customer_id INT,
            PRIMARY KEY (order_id, customer_id)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('orders', tables)
        self.assertEqual(primary_keys['orders'], ['order_id', 'customer_id'])
        self.assertNotIn('orders', foreign_keys)

    def test_primary_key_in_alter_table(self):
        sql_content = '''
        CREATE TABLE products (
            product_id INT,
            product_name VARCHAR(100)
        );

        ALTER TABLE products ADD CONSTRAINT pk_product PRIMARY KEY (product_id);
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('products', tables)
        self.assertEqual(primary_keys['products'], ['product_id'])
        self.assertNotIn('products', foreign_keys)

    def test_complex_column_definitions(self):
        sql_content = '''
        CREATE TABLE employees (
            emp_id INT PRIMARY KEY,
            emp_name VARCHAR(50) NOT NULL,
            hire_date DATE DEFAULT CURRENT_DATE,
            CONSTRAINT unique_emp UNIQUE (emp_name)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('employees', tables)
        self.assertEqual(primary_keys['employees'], ['emp_id'])
        self.assertNotIn('employees', foreign_keys)

    def test_quoted_identifiers_and_mixed_case(self):
        sql_content = '''
        CREATE TABLE "Employee Details" (
            "Emp_ID" INT PRIMARY KEY,
            "Emp_Name" VARCHAR(100)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('Employee Details', tables)
        self.assertEqual(primary_keys['Employee Details'], ['Emp_ID'])
        self.assertNotIn('Employee Details', foreign_keys)

    def test_foreign_key_with_multiple_columns(self):
        sql_content = '''
        CREATE TABLE order_items (
            order_id INT,
            item_id INT,
            PRIMARY KEY (order_id, item_id),
            FOREIGN KEY (order_id, item_id) REFERENCES orders(order_id, item_id)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('order_items', tables)
        self.assertEqual(primary_keys['order_items'], ['order_id', 'item_id'])
        self.assertIn('order_items', foreign_keys)
        self.assertEqual(foreign_keys['order_items'][0]['columns'], ['order_id', 'item_id'])
        self.assertEqual(foreign_keys['order_items'][0]['ref_table'], 'orders')
        self.assertEqual(foreign_keys['order_items'][0]['ref_columns'], ['order_id', 'item_id'])

    def test_foreign_key_with_schema_prefix(self):
        sql_content = '''
        CREATE TABLE payments (
            payment_id INT PRIMARY KEY,
            order_id INT,
            FOREIGN KEY (order_id) REFERENCES public.orders(order_id)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('payments', tables)
        self.assertEqual(primary_keys['payments'], ['payment_id'])
        self.assertIn('payments', foreign_keys)
        self.assertEqual(foreign_keys['payments'][0]['columns'], ['order_id'])
        self.assertEqual(foreign_keys['payments'][0]['ref_table'], 'orders')
        self.assertEqual(foreign_keys['payments'][0]['ref_columns'], ['order_id'])

    def test_multiple_foreign_key_constraints_in_alter_table(self):
        sql_content = '''
        CREATE TABLE shipments (
            shipment_id INT PRIMARY KEY,
            order_id INT,
            customer_id INT
        );

        ALTER TABLE shipments
            ADD CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
            ADD CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('shipments', tables)
        self.assertEqual(primary_keys['shipments'], ['shipment_id'])
        self.assertIn('shipments', foreign_keys)
        self.assertEqual(len(foreign_keys['shipments']), 2)
        self.assertEqual(foreign_keys['shipments'][0]['columns'], ['order_id'])
        self.assertEqual(foreign_keys['shipments'][0]['ref_table'], 'orders')
        self.assertEqual(foreign_keys['shipments'][0]['ref_columns'], ['order_id'])
        self.assertEqual(foreign_keys['shipments'][1]['columns'], ['customer_id'])
        self.assertEqual(foreign_keys['shipments'][1]['ref_table'], 'customers')
        self.assertEqual(foreign_keys['shipments'][1]['ref_columns'], ['customer_id'])

    def test_constraints_in_multiple_statements(self):
        sql_content = '''
        CREATE TABLE invoices (
            invoice_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT
        );

        ALTER TABLE invoices
            ADD CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('invoices', tables)
        self.assertEqual(primary_keys['invoices'], ['invoice_id'])
        self.assertIn('invoices', foreign_keys)
        self.assertEqual(foreign_keys['invoices'][0]['columns'], ['customer_id'])
        self.assertEqual(foreign_keys['invoices'][0]['ref_table'], 'customers')
        self.assertEqual(foreign_keys['invoices'][0]['ref_columns'], ['customer_id'])

    def test_sql_syntax_variations(self):
        sql_content = '''
        CREATE TABLE departments (
            dept_id INT PRIMARY KEY,
            dept_name VARCHAR(100)
        );

        ALTER TABLE departments ADD PRIMARY KEY (dept_id);
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('departments', tables)
        self.assertEqual(primary_keys['departments'], ['dept_id'])
        self.assertNotIn('departments', foreign_keys)

    def test_primary_key_and_foreign_key_in_create_table(self):
        sql_content = '''
        CREATE TABLE orders (
            order_id INT,
            customer_id INT,
            PRIMARY KEY (order_id),
            CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('orders', tables)
        self.assertEqual(primary_keys['orders'], ['order_id'])
        self.assertIn('orders', foreign_keys)
        self.assertEqual(foreign_keys['orders'][0]['columns'], ['customer_id'])
        self.assertEqual(foreign_keys['orders'][0]['ref_table'], 'customers')
        self.assertEqual(foreign_keys['orders'][0]['ref_columns'], ['customer_id'])

    def test_mixed_primary_key_and_foreign_key_definitions(self):
        sql_content = '''
        CREATE TABLE products (
            product_id INT PRIMARY KEY,
            category_id INT,
            CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categories(category_id)
        );

        CREATE TABLE categories (
            category_id INT PRIMARY KEY,
            category_name VARCHAR(100)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('products', tables)
        self.assertEqual(primary_keys['products'], ['product_id'])
        self.assertIn('products', foreign_keys)
        self.assertEqual(foreign_keys['products'][0]['columns'], ['category_id'])
        self.assertEqual(foreign_keys['products'][0]['ref_table'], 'categories')
        self.assertEqual(foreign_keys['products'][0]['ref_columns'], ['category_id'])
        self.assertIn('categories', tables)
        self.assertEqual(primary_keys['categories'], ['category_id'])

    def test_no_primary_key_defined(self):
        sql_content = '''
        CREATE TABLE employees (
            emp_id INT,
            emp_name VARCHAR(50)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('employees', tables)
        self.assertEqual(primary_keys['employees'], [])
        self.assertNotIn('employees', foreign_keys)

    def test_unique_constraints_and_composite_unique_keys(self):
        sql_content = '''
        CREATE TABLE inventory (
            item_id INT,
            warehouse_id INT,
            quantity INT,
            PRIMARY KEY (item_id),
            CONSTRAINT unique_warehouse_item UNIQUE (warehouse_id, item_id)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('inventory', tables)
        self.assertEqual(primary_keys['inventory'], ['item_id'])
        self.assertNotIn('inventory', foreign_keys)

    def test_foreign_key_with_different_references_and_constraint_names(self):
        sql_content = '''
        CREATE TABLE orders (
            order_id INT PRIMARY KEY,
            customer_id INT,
            CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES clients(client_id)
        );

        CREATE TABLE clients (
            client_id INT PRIMARY KEY,
            client_name VARCHAR(100)
        );

        ALTER TABLE orders ADD CONSTRAINT fk_client FOREIGN KEY (customer_id) REFERENCES clients(client_id);
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('orders', tables)
        self.assertEqual(primary_keys['orders'], ['order_id'])
        self.assertIn('orders', foreign_keys)
        self.assertEqual(foreign_keys['orders'][0]['columns'], ['customer_id'])
        self.assertEqual(foreign_keys['orders'][0]['ref_table'], 'clients')
        self.assertEqual(foreign_keys['orders'][0]['ref_columns'], ['client_id'])

    def test_sql_dialects_and_variants(self):
        sql_content = '''
        CREATE TABLE items (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(255)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('items', tables)
        self.assertEqual(primary_keys['items'], ['item_id'])
        self.assertNotIn('items', foreign_keys)

    def test_mixed_data_types_and_constraints(self):
        sql_content = '''
        CREATE TABLE orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            order_date DATE DEFAULT CURRENT_DATE,
            customer_id INT,
            CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE customers (
            customer_id INT PRIMARY KEY,
            customer_name VARCHAR(255)
        );
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('orders', tables)
        self.assertEqual(primary_keys['orders'], ['order_id'])
        self.assertIn('orders', foreign_keys)
        self.assertEqual(foreign_keys['orders'][0]['columns'], ['customer_id'])
        self.assertEqual(foreign_keys['orders'][0]['ref_table'], 'customers')
        self.assertEqual(foreign_keys['orders'][0]['ref_columns'], ['customer_id'])
        self.assertIn('customers', tables)
        self.assertEqual(primary_keys['customers'], ['customer_id'])

    def test_drop_and_alter_statements(self):
        sql_content = '''
        CREATE TABLE temp_orders (
            order_id INT,
            PRIMARY KEY (order_id)
        );

        ALTER TABLE temp_orders DROP PRIMARY KEY;
        ALTER TABLE temp_orders ADD CONSTRAINT pk_order PRIMARY KEY (order_id);
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('temp_orders', tables)
        self.assertEqual(primary_keys['temp_orders'], ['order_id'])
        self.assertNotIn('temp_orders', foreign_keys)

    def test_sql_statements_with_comments(self):
        sql_content = '''
        -- Create table for storing orders
        CREATE TABLE orders (
            order_id INT PRIMARY KEY, -- Primary key for orders
            customer_id INT
        );

        -- Foreign key constraint
        ALTER TABLE orders ADD CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
        '''
        tables, primary_keys, foreign_keys = self.run_parser(sql_content)
        self.assertIn('orders', tables)
        self.assertEqual(primary_keys['orders'], ['order_id'])
        self.assertIn('orders', foreign_keys)
        self.assertEqual(foreign_keys['orders'][0]['columns'], ['customer_id'])
        self.assertEqual(foreign_keys['orders'][0]['ref_table'], 'customers')
        self.assertEqual(foreign_keys['orders'][0]['ref_columns'], ['customer_id'])

if __name__ == "__main__":
    unittest.main()
