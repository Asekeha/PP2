import psycopg2
from config import load_config
import os

def setup_database():
    # Creates the table and loads functions/procedures from SQL files
    create_table_command = """
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(50) NOT NULL UNIQUE
    )
    """
    conn = None
    try:
        conn = psycopg2.connect(**load_config())
        cur = conn.cursor()
        
        # Create table
        cur.execute(create_table_command)
        
        # Read and execute functions
        if os.path.exists('functions.sql'):
            with open('functions.sql', 'r', encoding='utf-8') as f:
                cur.execute(f.read())
                
        # Read and execute procedures
        if os.path.exists('procedures.sql'):
            with open('procedures.sql', 'r', encoding='utf-8') as f:
                cur.execute(f.read())
                
        conn.commit()
        print("Database, functions, and procedures successfully initialized!")
        
    except Exception as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    setup_database()
