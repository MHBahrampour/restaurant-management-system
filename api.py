import psycopg2
from config import config

def get_data():
    """ Get data for a table """

    # List of tables and columns
    tables_columns = {
        "branch":       ("id", "name", "state", "city", "street", "date"),
        "person":       ("id", "firt_name", "last_name", "gender", "phone_number"),
        "employee":     ("id", "branch_id", "post", "degree", "birth_date", "salary", "state", "married"),
        "customer":     ("id",),
        "salon":        ("id", "capacity", "type", "floor"),
        "orders":       ("customer_id", "waiter_id", "accountant_id", "salon_id", "order_date", "reg_time", "total_cost"),
        "food":         ("id", "chef_id", "name", "type", "cost"),
        "order_foods":  ("order_id", "food_id")        
    }

    print("""
    :: Select number of the table: 
       1. branch    2. person    3. employee    4. customer
       5. salon     6. orders    7. food        8. order_foods
    """)

    table_number = int(input(">> Enter the table number: "))
    table_name = list(tables_columns.keys())[table_number-1]

    row = []
    print(":: Insert data for each column: ")

    for column in tables_columns[table_name]:
        tmp = input(">> Column '{}': ".format(column))

        # Casting data into the correct type
        if ("id" in column) or (column in ("capacity", "floor")):
            tmp = int(tmp)
        if column in ("salary", "total_cost", "cost"):
            tmp = float(tmp)

        row.append(tmp)

    return table_name, tuple(row)

def insert_row(table_name, row):
    """ Insert a row into a table """

    sql = {
        "branch":       "INSERT INTO branch VALUES(%s, %s, %s, %s, %s, %s)",
        "person":       "INSERT INTO person VALUES(%s, %s, %s, %s, %s)",
        "employee":     "INSERT INTO employee VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
        "customer":     "INSERT INTO customer VALUES(%s)",
        "salon":        "INSERT INTO salon VALUES(%s, %s, %s, %s)",
        "orders":       "INSERT INTO orders VALUES(DEFAULT, %s, %s, %s, %s, %s, %s, %s)",
        "food":         "INSERT INTO food VALUES(%s, %s, %s, %s, %s)",
        "order_foods":  "INSERT INTO order_foods VALUES(DEFAULT, %s, %s)"
    }

    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql[table_name], row)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def main():
    print("""
    :: Use belows numbers to do something: 
       1 - Insert data into a table.
       0 - Close the app.""")

    while True:

        user_input = input("\n>> ")

        if user_input == '1':
            table_name, row = get_data()
            insert_row(table_name, row)
        elif user_input == '0':
            print("!! API closed.")
            exit()

if __name__ == '__main__':
    main()