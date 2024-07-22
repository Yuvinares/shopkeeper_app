import sqlite3


def connect_db(db_name='shopkeeper.db'):
    """Connect to the SQLite database."""
    return sqlite3.connect(db_name)


def create_tables(conn):
    """Create the 'products' and 'sales' tables if they don't exist."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    conn.commit()


def add_product(conn):
    """Add a new product or update the quantity of an existing product."""
    name = input("Enter product name: ")
    price = float(input("Enter product price: "))
    quantity = int(input("Enter product quantity: "))
    cursor = conn.cursor()

    cursor.execute('SELECT id, quantity FROM products WHERE name = ?', (name,))
    product = cursor.fetchone()

    if product:
        product_id, existing_quantity = product
        new_quantity = existing_quantity + quantity
        cursor.execute('''
            UPDATE products
            SET quantity = ?, price = ?
            WHERE id = ?
        ''', (new_quantity, price, product_id))
        print(f"Updated {name}: new quantity = {new_quantity}")
    else:
        cursor.execute('''
            INSERT INTO products (name, price, quantity)
            VALUES (?, ?, ?)
        ''', (name, price, quantity))
        print(f"Added new product: {name}")

    conn.commit()
    print("Product added successfully.")


def retrieve_products(conn):
    """Retrieve all products from the 'products' table."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    return cursor.fetchall()


def make_sale(conn):
    """Record a sale and update the product quantity."""
    product_id = int(input("Enter product ID: "))
    quantity = int(input("Enter quantity sold: "))

    cursor = conn.cursor()

    cursor.execute(
        'SELECT price, quantity FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()

    if product is None:
        print("Product not found.")
        return

    price, available_quantity = product

    if quantity > available_quantity:
        print("Not enough stock.")
        return

    total = price * quantity

    cursor.execute('''
        INSERT INTO sales (product_id, quantity, total)
        VALUES (?, ?, ?)
    ''', (product_id, quantity, total))

    cursor.execute('''
        UPDATE products
        SET quantity = quantity - ?
        WHERE id = ?
    ''', (quantity, product_id))

    conn.commit()
    print("Sale recorded successfully.")


def retrieve_sales(conn):
    """Retrieve all sales from the 'sales' table."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, p.name, s.quantity, s.total
        FROM sales s
        JOIN products p ON s.product_id = p.id
    ''')
    return cursor.fetchall()


def print_products(products):
    """Print all products in a readable format."""
    print("ID | Name            | Price | Quantity")
    print("----------------------------------------")
    for product in products:
        print(f"{product[0]:<2} | {product[1]:<15} | {
              product[2]:<5} | {product[3]:<8}")


def print_sales(sales):
    """Print all sales in a readable format."""
    print("ID | Product Name    | Quantity | Total")
    print("----------------------------------------")
    for sale in sales:
        print(f"{sale[0]:<2} | {sale[1]:<15} | {sale[2]:<8} | {sale[3]:<5}")


def menu():
    """Display the menu and handle user input."""
    conn = connect_db()
    create_tables(conn)

    while True:
        print("\nShopkeeper Application")
        print("1. Add Product")
        print("2. View Products")
        print("3. Make Sale")
        print("4. View Sales")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_product(conn)
        elif choice == '2':
            print("Current Products:")
            products = retrieve_products(conn)
            print_products(products)
        elif choice == '3':
            make_sale(conn)
        elif choice == '4':
            print("Sales Made:")
            sales = retrieve_sales(conn)
            print_sales(sales)
        elif choice == '5':
            print("Exiting the application.")
            conn.close()
            break
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == '__main__':
    menu()
