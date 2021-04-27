from configparser import ConfigParser
import psycopg2

# Read the Database file and return connection parameters
def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

# Connect to the PostgreSQL database server
def connect():

    conn = None
    try:
        # Read connection parameters
        params = config()

        # Connect to the PostgreSQL server
        print(':: Connecting to the PostgreSQL database ...\n')
        conn = psycopg2.connect(**params)
		
        # Create a cursor
        cur = conn.cursor()
        
	    # Execute a statement
        print(':: PostgreSQL database version:')
        cur.execute('SELECT version()')

        # Display the PostgreSQL database server version
        db_version = cur.fetchone()
        print("   {0}".format(db_version) + "\n")
       
	    # Close the communication with the PostgreSQL
        cur.close()

        return True

    except (Exception, psycopg2.DatabaseError) as error:
        print("!! {0}".format(error))
        
        return False

    finally:
        if conn is not None:
            conn.close()
            print(":: Database connection closed.")

# Create tables in the PostgreSQL database
def create_tables():

    commands = (
        """
        CREATE TABLE IF NOT EXISTS branch (
            id              INTEGER NOT NULL PRIMARY KEY,
            name            TEXT NOT NULL,
            state           TEXT NOT NULL,
            city            TEXT NOT NULL,
            street          TEXT NOT NULL,
            date            DATE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS person (
            id              INTEGER NOT NULL PRIMARY KEY,
            firt_name       TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            gender          TEXT NOT NULL,
            phone_number    TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS employee (
            id              INTEGER PRIMARY KEY,
            branch_id       INTEGER NOT NULL,
            post            TEXT NOT NULL,
            degree          TEXT NOT NULL,
            birth_date      DATE NOT NULL,
            salary          REAL NOT NULL,
            state           TEXT NOT NULL,
            married         TEXT NOT NULL,

            CONSTRAINT fk_person
                FOREIGN KEY (id)
                    REFERENCES person (id)
                    ON UPDATE CASCADE ON DELETE CASCADE,

            CONSTRAINT fk_branch
                FOREIGN KEY (branch_id)
                    REFERENCES branch (id)
                    ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS customer (
            id              INTEGER PRIMARY KEY,

            CONSTRAINT fk_person
                FOREIGN KEY (id)
                    REFERENCES person (id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS salon (
            id              INTEGER NOT NULL PRIMARY KEY,
            capacity        INTEGER NOT NULL,
            type            TEXT NOT NULL,
            floor           INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            id              SERIAL PRIMARY KEY,
            customer_id     INTEGER NOT NULL,
            waiter_id       INTEGER NOT NULL,
            accountant_id   INTEGER NOT NULL,
            salon_id        INTEGER NOT NULL,
            order_date      DATE NOT NULL,
            reg_time        TIME NOT NULL,
            total_cost      REAL NOT NULL,

            CONSTRAINT fk_customer
                FOREIGN KEY (customer_id)
                    REFERENCES customer (id)
                    ON DELETE CASCADE,

            CONSTRAINT fk_employee
                FOREIGN KEY (waiter_id)
                    REFERENCES employee (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (accountant_id)
                    REFERENCES employee (id)
                    ON DELETE CASCADE,
            CONSTRAINT fk_salon
                FOREIGN KEY (salon_id)
                    REFERENCES salon (id)
                    ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS food (
            id              INTEGER NOT NULL PRIMARY KEY,
            chef_id         INTEGER NOT NULL,
            name            TEXT NOT NULL,
            type            TEXT NOT NULL,
            cost            REAL NOT NULL,

            CONSTRAINT fk_employee
                FOREIGN KEY (chef_id)
                    REFERENCES employee (id)
                    ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_foods (
            id              SERIAL PRIMARY KEY,
            order_id        INTEGER NOT NULL,
            food_id         INTEGER NOT NULL,

            CONSTRAINT fk_orders
                FOREIGN KEY (order_id)
                    REFERENCES orders (id)
                    ON DELETE CASCADE,

            CONSTRAINT fk_food
                FOREIGN KEY (food_id)
                    REFERENCES food (id)
                    ON DELETE CASCADE
        )
        """,     
    )

    conn = None
    try:
        # read the connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # create table one by one
        for command in commands:
            cur.execute(command)

        # close communication with the PostgreSQL database server
        cur.close()

        # commit the changes
        conn.commit()

        # Execute a statement
        print(":: All tables created successfully.\n")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

# Insert multiple row into tables
def insert_data(table_name, data_list):

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
        cur.executemany(sql[table_name], data_list)

        # commit the changes to the database
        conn.commit()

        # close communication with the database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

# Initialize data for tables         
def initialize_data():
    
    print(":: Inserting sample data ...")
    # Table 'branch'
    data_list = [
        (96101,     "BestFood_1",   "Tehran",       "Varamin",      "Zeytoun",      "1390-11-05"),
        (95053,     "BestFood_2",   "Kerman",       "Sirjan",       "AhmadKafi",    "1393-08-27"),
        (94017,     "BestFood_3",   "Fars",         "Shiraz",       "SattarKhan",   "1396-10-20")
    ]
    insert_data("branch", data_list)
    print("   [Done] Inserting to 'branch'")
    
    # Table 'person'
    data_list = [
        (13114,     "Mostafa",      "Mirzaee",      "male",         9177463827),
        (13119,     "Mahsa",        "Kazemi",       "female",       9171349865),
        (13127,     "Reza",         "Hosseini",     "male",         9178472313),
        (13835,     "Zohre",        "Maleki",       "female",       9177564390),
        (13877,     "Helen",        "Salehi",       "female",       9379862512),
        (23814,     "Ahmad",        "Mirzaee",      "male",         9165342198),

        (23819,     "Mahdi",        "Aghhaee",      "male",         9168348278),
        (23827,     "Mohsen",       "Karami",       "male",         9178739284),
        (23835,     "Minoo",        "Maleki",       "female",       9168344678),
        (23877,     "Zahra",        "Salehi",       "female",       9378656253),
        (24114,     "Mostafa",      "Mirzaee",      "male",         9437571675),
        (24119,     "Mohsen",       "Aghhaee",      "male",         9075848743),

        (24127,     "Reza",         "Karami",       "male",         9187567151),
        (25835,     "Zohre",        "Maleki",       "female",       9187457234),
        (25877,     "Helen",        "Salehi",       "female",       9276578145),
        (35134,     "Mohammad",     "Mohammadian",  "male",         9175815143),
        (35178,     "Ali",          "Rezazadeh",    "male",         9131113834),
        (35198,     "Amir",         "Ahmadi",       "male",         9814871119),

        (77211,     "Shabnam",      "Ahmadi",       "female",       9148271589),
        (77278,     "Ali",          "Alizadeh",     "male",         9009128115),
        (77587,     "Mona",         "Karami",       "female",       9184175185),
        (88578,     "Golnaz",       "Mirzaee",      "female",       9127587145),
        (88175,     "Reza",         "Farhadi",      "male",         9018574514),
        (88154,     "Mohsen",       "Fattahi",      "male",         9857185975),
        (99870,     "Rozhin",       "Mohammadian",  "female",       9825719501),
        (99128,     "Afshin",       "Niknam",       "male",         9158719511),
        (99137,     "Negar",        "Alizadeh",     "female",       9185894115)
    ]
    insert_data("person", data_list)
    print("   [Done] Inserting to 'person'")
    
    # Table 'employee'
    data_list = [
        (13114,      96101,       "Manager",        "Master",       "1367-09-27",     "950",       "Tehran",     "Yes"),
        (13119,      96101,       "Waiter",         "Associate",    "1369-03-09",     "200",       "Tehran",     "Yes"),
        (13127,      96101,       "Waiter",         "Diploma",      "1371-02-14",     "200",       "Tehran",     "No"),
        (13835,      96101,       "Chef",           "Bachelor",     "1370-08-19",     "400",       "Tehran",     "Yes"),
        (13877,      96101,       "Chef",           "Diploma",      "1363-04-10",     "400",       "Tehran",     "No"),
        (23814,      96101,       "Accountants",    "Master",       "1361-01-17",     "500",       "Tehran",     "Yes"),

        (23819,      95053,       "Manager",        "Master",       "1361-02-15",     "850",       "Kerman",     "Yes"),
        (23827,      95053,       "Waiter",         "Associate",    "1364-01-11",     "200",       "Kerman",     "Yes"),
        (23835,      95053,       "Waiter",         "Diploma",      "1365-04-09",     "200",       "Kerman",     "No"),
        (23877,      95053,       "Chef",           "Bachelor",     "1371-07-06",     "350",       "Kerman",     "Yes"),
        (24114,      95053,       "Chef",           "Diploma",      "1372-09-14",     "350",       "Kerman",     "No"),
        (24119,      95053,       "Accountants",    "Master",       "1374-12-28",     "450",       "Kerman",     "Yes"),

        (24127,      94017,       "Manager",        "Master",       "1360-09-29",     "900",       "Kerman",     "Yes"),
        (25835,      94017,       "Waiter",         "Associate",    "1370-09-21",     "200",       "Kerman",     "Yes"),
        (25877,      94017,       "Waiter",         "Diploma",      "1363-09-23",     "200",       "Kerman",     "No"),
        (35134,      94017,       "Chef",           "Bachelor",     "1369-09-22",     "350",       "Kerman",     "Yes"),
        (35178,      94017,       "Chef",           "Diploma",      "1370-09-14",     "350",       "Kerman",     "No"),
        (35198,      94017,       "Accountants",    "Master",       "1371-09-02",     "500",       "Kerman",     "Yes")
    ]
    insert_data("employee", data_list)
    print("   [Done] Inserting to 'employee'")

    # Table 'customer'
    data_list = [
        (24127,),
        (25835,),
        (25877,),
        (35134,),
        (35178,),
        (35198,),
    ]
    insert_data("customer", data_list)
    print("   [Done] Inserting to 'customer'")

    # Table 'salon'
    data_list = [
        (101,    20,     "Class A",    1),
        (102,    50,     "Class B",    2),
        (103,    100,    "Class C",    3),

        (201,    20,     "Class A",    1),
        (202,    50,     "Class B",    2),
        (203,    100,    "Class C",    3),

        (301,    20,     "Class A",    1),
        (302,    50,     "Class B",    2),
        (303,    100,    "Class C",    3)
    ]
    insert_data("salon", data_list)
    print("   I[Done] nserting to 'salon'")

    # Table 'orders'
    data_list = [
        (24127,    13119,    23814,    101,    "1399-11-07",    "06:05 PM",    75000),
        (25835,    13127,    23814,    102,    "1400-01-03",    "11:30 AM",    55000),
        (24127,    13127,    23814,    103,    "1400-01-03",    "04:50 PM",    40000),

        (25877,    23827,    24119,    102,    "1399-10-03",    "12:45 PM",    80000),
        (35134,    23835,    24119,    101,    "1399-12-29",    "01:00 PM",    40000),

        (35178,    25835,    35198,    101,    "1399-11-01",    "08:00 PM",    60000),
        (35198,    25877,    35198,    103,    "1400-01-02",    "09:10 PM",    15000),
    ]
    insert_data("orders", data_list)
    print("   [Done] Inserting to 'orders'")

    # Table 'food'
    data_list = [
        (961,    13835,    "Chelo Morgh",    "Food",        25000),
        (962,    13835,    "Chelo Kabab",    "Food",        35000),
        (963,    13877,    "Pizza",          "FastFood",    20000),
        (964,    13877,    "Hot Dog",        "FastFood",    15000),

        (951,    23877,    "Chelo Morgh",    "Food",        25000),
        (952,    23877,    "Chelo Kabab",    "Food",        35000),
        (953,    24114,    "Pizza",          "FastFood",    20000),
        (954,    24114,    "Hot Dog",        "FastFood",    15000),

        (941,    35134,    "Chelo Morgh",    "Food",        25000),
        (942,    35134,    "Chelo Kabab",    "Food",        35000),
        (943,    35178,    "Pizza",          "FastFood",    20000),
        (944,    35178,    "Hot Dog",        "FastFood",    15000),
    ]
    insert_data("food", data_list)
    print("   [Done] Inserting to 'food'")

    # Table 'order_foods'
    data_list = [
        (1,    961),
        (1,    962),
        (1,    964),
        (2,    962),
        (2,    963),
        (3,    961),
        (3,    964),
        (4,    963),
        (4,    951),
        (4,    952),
        (5,    954),
        (5,    951),
        (6,    942),
        (6,    941),
        (7,    944)
    ]
    insert_data("order_foods", data_list)
    print("   [Done] Inserting to 'order_foods'")