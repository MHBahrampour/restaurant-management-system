import psycopg2
from config import config

def create_tables():
    """ create tables in the PostgreSQL database"""

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

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()