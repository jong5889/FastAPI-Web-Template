import os
import psycopg2
from dotenv import load_dotenv

def connect_to_supabase():
    """
    Connect to the Supabase PostgreSQL database using environment variables.
    
    Returns:
        conn: A database connection object if successful, None otherwise.
    """
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Get database credentials from environment variables
        db_config = {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        }
        
        # Create a connection to the database
        conn = psycopg2.connect(**db_config)
        print("✅ Successfully connected to Supabase!")
        return conn
    
    except psycopg2.Error as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return None

def test_connection():
    """Test the database connection and print database version."""
    conn = connect_to_supabase()
    if conn:
        try:
            with conn.cursor() as cur:
                # Execute a simple query
                cur.execute("SELECT version();")
                db_version = cur.fetchone()
                print(f"\n📊 Database Version: {db_version[0]}")
                
                # List all tables (if any exist)
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                tables = cur.fetchall()
                
                if tables:
                    print("\n📋 Tables in the database:")
                    for table in tables:
                        print(f"- {table[0]}")
                else:
                    print("\nℹ️ No tables found in the database.")
                    
        except Exception as e:
            print(f"❌ Error executing query: {e}")
        finally:
            # Close the connection
            conn.close()
            print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    print("🚀 Attempting to connect to Supabase...")
    test_connection()
