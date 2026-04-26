import psycopg2
import os
from config import load_config


def get_connection():
    """Returns a new database connection."""
    try:
        return psycopg2.connect(**load_config())
    except Exception as error:
        print(f"Connection error: {error}")
        return None


def setup_database():
    """
    Creates ALL tables from scratch and loads SQL files.
    Run this once before using the app.
    """
    conn = None
    try:
        conn = psycopg2.connect(**load_config())
        cur = conn.cursor()

        # 1. Groups table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id   SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """)

        # 2. Seed default groups
        cur.execute("""
            INSERT INTO groups (name)
            VALUES ('Family'), ('Work'), ('Friend'), ('Other')
            ON CONFLICT (name) DO NOTHING
        """)

        # 3. Main contacts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id       SERIAL PRIMARY KEY,
                name     VARCHAR(255) NOT NULL UNIQUE,
                email    VARCHAR(100),
                birthday DATE,
                group_id INTEGER REFERENCES groups(id)
            )
        """)

        # 4. Phones table (many phones per contact)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id         SERIAL PRIMARY KEY,
                contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
                phone      VARCHAR(20) NOT NULL,
                type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
            )
        """)

        # 5. Load procedures and functions from SQL file
        if os.path.exists('procedures.sql'):
            with open('procedures.sql', 'r', encoding='utf-8') as f:
                cur.execute(f.read())

        conn.commit()
        print("Database setup complete! All tables and procedures are ready.")

    except Exception as error:
        print(f"Setup error: {error}")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    setup_database()
