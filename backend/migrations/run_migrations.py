"""
Database migration runner
Executes SQL migration files in order
"""
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    """Run all SQL migration files in order"""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("Error: DATABASE_URL not set in environment")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Get migration directory
        migrations_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get all SQL files sorted by name
        sql_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        print(f"\nFound {len(sql_files)} migration files")
        
        # Execute each migration
        for sql_file in sql_files:
            file_path = os.path.join(migrations_dir, sql_file)
            
            print(f"\nExecuting: {sql_file}")
            
            with open(file_path, 'r') as f:
                sql_content = f.read()
                
            try:
                cursor.execute(sql_content)
                print(f"✓ {sql_file} executed successfully")
            except Exception as e:
                print(f"✗ Error executing {sql_file}: {e}")
                raise
        
        print("\n✓ All migrations completed successfully!")
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    run_migrations()
