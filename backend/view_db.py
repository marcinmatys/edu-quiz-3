import sqlite3
import os
from pathlib import Path

# Get the absolute path to the database file
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "edu-quiz.db"

# Check if the database file exists
if not os.path.exists(DB_PATH):
    print(f"Database file not found: {DB_PATH}")
    exit(1)

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Function to display table names
def show_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    if tables:
        print("\nTables in the database:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table[0]}")
    else:
        print("No tables found in the database.")
    return [table[0] for table in tables]

# Function to display table schema
def show_schema(table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    if columns:
        print(f"\nSchema for table '{table_name}':")
        print("Column Name".ljust(20) + "Type".ljust(15) + "Not Null".ljust(10) + "Default Value".ljust(15) + "Primary Key")
        print("-" * 70)
        for col in columns:
            print(f"{col[1]}".ljust(20) + f"{col[2]}".ljust(15) + f"{col[3]}".ljust(10) + f"{col[4] or 'None'}".ljust(15) + f"{col[5]}")
    else:
        print(f"No schema found for table '{table_name}'.")

# Function to display table content
def show_content(table_name, limit=10):
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]
        
        if rows:
            print(f"\nContent of table '{table_name}' (first {limit} rows):")
            # Print column headers
            header = " | ".join(str(col).ljust(15) for col in columns)
            print(header)
            print("-" * len(header))
            
            # Print rows
            for row in rows:
                print(" | ".join(str(val).ljust(15) for val in row))
            
            # Count total rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            total_rows = cursor.fetchone()[0]
            print(f"\nTotal rows in table: {total_rows}")
        else:
            print(f"No data found in table '{table_name}'.")
    except sqlite3.Error as e:
        print(f"Error retrieving data: {e}")

# Main interactive loop
def main():
    print("=== SQLite Database Viewer ===")
    print(f"Database: {DB_PATH}")
    
    while True:
        print("\n--- Main Menu ---")
        print("1. List all tables")
        print("2. View table schema")
        print("3. View table content")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-3): ")
        
        if choice == "0":
            break
        elif choice == "1":
            show_tables()
        elif choice == "2":
            tables = show_tables()
            if tables:
                table_choice = input("\nEnter table number or name: ")
                try:
                    # Check if input is a number
                    idx = int(table_choice) - 1
                    if 0 <= idx < len(tables):
                        show_schema(tables[idx])
                    else:
                        print("Invalid table number.")
                except ValueError:
                    # Input is a name
                    if table_choice in tables:
                        show_schema(table_choice)
                    else:
                        print("Invalid table name.")
        elif choice == "3":
            tables = show_tables()
            if tables:
                table_choice = input("\nEnter table number or name: ")
                try:
                    # Check if input is a number
                    idx = int(table_choice) - 1
                    if 0 <= idx < len(tables):
                        show_content(tables[idx])
                    else:
                        print("Invalid table number.")
                except ValueError:
                    # Input is a name
                    if table_choice in tables:
                        show_content(table_choice)
                    else:
                        print("Invalid table name.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    finally:
        # Clean up
        cursor.close()
        conn.close()
        print("\nDatabase connection closed.") 