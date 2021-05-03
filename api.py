import psycopg2
import library as lib

# Get data for tables
def get_data():

    # List of tables and columns
    tables_columns = {
        "branch":       ("id", "name", "state", "city", "street", "date"),
        "person":       ("id", "firt_name", "last_name", "gender", "phone_number"),
        "employee":     ("id", "branch_id", "post", "degree", "birth_date", "salary", "state", "married"),
        "customer":     ("id",),
        "salon":        ("id", "capacity", "type", "floor"),
        "orders":       ("customer_id", "waiter_id", "accountant_id", "salon_id", "order_date", "reg_time", "total_cost"),
        "food":         ("id", "branch_id", "chef_id", "name", "type", "cost"),
        "order_foods":  ("order_id", "food_id")        
    }

    print(":: Select number of the table:")
    print("   1. branch    2. person    3. employee    4. customer")
    print("   5. salon     6. orders    7. food        8. order_foods\n")

    table_number = int(input(">> Enter the table number: "))
    table_name = list(tables_columns.keys())[table_number-1]

    row = []
    print(":: Inserting data for '{}':".format(table_name))

    for column in tables_columns[table_name]:
        tmp = input(">> Column '{}': ".format(column))

        # Casting data into the correct type
        if ("id" in column) or (column in ("capacity", "floor")):
            tmp = int(tmp)
        if column in ("salary", "total_cost", "cost"):
            tmp = float(tmp)

        row.append(tmp)

    return table_name, tuple(row)

# Insert a row into tables
def insert_row(table_name, row):

    sql = {
        "branch":       "INSERT INTO branch VALUES(%s, %s, %s, %s, %s, %s)",
        "person":       "INSERT INTO person VALUES(%s, %s, %s, %s, %s)",
        "employee":     "INSERT INTO employee VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
        "customer":     "INSERT INTO customer VALUES(%s)",
        "salon":        "INSERT INTO salon VALUES(%s, %s, %s, %s)",
        "orders":       "INSERT INTO orders VALUES(DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)",
        "food":         "INSERT INTO food VALUES(%s, %s, %s, %s, %s, %s)",
        "order_foods":  "INSERT INTO order_foods VALUES(DEFAULT, %s, %s)"
    }

    conn = None
    try:
        # read database configuration
        params = lib.config()
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

# This function, initialize a complete sample database
def sample_database():
    check = lib.connect()
    if check == True:
        lib.create_tables()
        lib.initialize_data()

def sample_queries():

    queries = [
        """
            SELECT	
                id, first_name || ' ' || last_name AS full_name, gender
            FROM
                person
            WHERE
                id IN (
                    SELECT id FROM employee
                )
            ORDER BY	
                gender asc
        """,

        """
            SELECT	
                food.name, branch.name, cost
            FROM
                food
            INNER JOIN
                branch
                ON branch_id = branch.id
            WHERE
                cost between 10000 and 20000
            ORDER BY	
                food.name asc
        """,

        """
            SELECT	
                branch.name AS branch_name,
                first_name || ' ' || last_name AS full_name,
                phone_number,
                SUM(total_cost) AS total_purchase,
                COUNT(orders.id) AS purchase_count                
            FROM 
                ((orders
            INNER JOIN
                person
                ON orders.customer_id = person.id)
            INNER JOIN
                branch
                ON branch_id = branch.id)
            WHERE
                branch.name = 'BestFood_1'
            GROUP BY
                branch.name, full_name, phone_number
            ORDER BY	
                total_purchase desc
            FETCH FIRST 1 ROW ONLY
        """,

        """
            SELECT
                name AS branch_name,
                COUNT(orders.id),
                SUM(total_cost) AS purchase
            FROM
                orders
            LEFT OUTER JOIN
                branch
                ON branch_id = branch.id
            WHERE
                order_date >= '1400-01-01'
            GROUP BY
                branch_name
            HAVING
                SUM(total_cost) >= 0
            ORDER BY
                branch_name
        """,

        """
            SELECT
                first_name || ' ' || last_name AS full_name,
                branch.name,
                COUNT(food_id) AS count
            FROM
                ((((food
            INNER JOIN
                order_foods
                ON food.id = food_id)
            INNER JOIN
                person
                ON person.id = chef_id)
            INNER JOIN
                employee
                ON chef_id = employee.id)
            INNER JOIN
                branch
                ON employee.branch_id = branch.id)
            GROUP BY
                full_name, branch.name
            ORDER BY
                count DESC
        """
    ]

    print(":: List of all Sample Queries:")
    print("   1. ID, Full Name and Gender of all employees.")
    print("   2. Food Name, Branch Name and price of foods that are priced between 10000 and 20000.")
    print("   3. Branch Name, Full Name, and Total Purchase of #1 buyer of branch 'BestFood_1'.")
    print("   4. Branch Name, Order Count and Income of all branches in 1400.")
    print("   5. Full Name, Branch Name and count of cooking of the chefs who cooked the most food.")

    query_number = int(input(">> Enter the query number to display the result: "))

    rows = lib.execute_query(queries[query_number-1])

    for row in rows:
        print("   {}".format(row))

def main():

    print("""
    :: Use belows numbers to do something: 
       0 - Initialize a complete sample database.
       1 - Insert data into a table.
       2 - Sample Queries.
       9 - Close the app.""")

    # Initialization of sample database
    init = False

    while True:

        user_input = input("\n>> ")

        if user_input == '0':
            if init == False:
                sample_database()
                init = True
            else:
                print(":: Sample database is already created.")

        elif user_input == '1':
            table_name, row = get_data()
            insert_row(table_name, row)

        elif user_input == '2':
            sample_queries()

        elif user_input == '9':
            print("!! API closed.")
            exit()

if __name__ == '__main__':
    main()